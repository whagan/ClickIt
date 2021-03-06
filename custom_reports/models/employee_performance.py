from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime
from odoo.exceptions import ValidationError
import datetime

# Employee Performance Report DataModel (Main Report)
class EmployeePerformanceReport(models.Model):
    _name = 'custom_reports.employee_performance_report'
    _description = "Employee Performance Report"
    _rec_name = 'report_title'
    
    # basic properties
    report_title = fields.Char('Report Title', required=True)
    start_date = fields.Datetime(string='Start Date', required=True, ValidationError='_check_date_validity')
    end_date = fields.Datetime(string='End Date', required=True, ValidationError='_check_date_validity')
    employee_ids = fields.Many2many('hr.employee', relation='custom_reports_employee_report_rel', column1='custom_report_id', column2='employee_id', string="Employees")
    employee_performance_ids = fields.One2many('custom_reports.employee_performance', 'employee_performance_report_id', string="Employee Performances")
    employee_performance_graph = fields.Text('Employee Graph', default='EmployeeGraph')
    
    # methods
    # create override would add all of the items on the list to the subreport's list
    @api.model
    def create(self, values):
        record = super(EmployeePerformanceReport, self).create(values)
        employee_ids = values['employee_ids'][0][2]
        records = []
        for employee_id in employee_ids:
            records.append({
                'employee_id': employee_id,
                'employee_performance_report_id': record.id,
                'start_date': record.start_date,
                'end_date': record.end_date
            })
        self.env['custom_reports.employee_performance'].create(records)
        return record

    # write override would adds and removes items on the subreport based on the whether items are in the new values or not 
    def write(self, values):
        record = super(EmployeePerformanceReport, self).write(values)
        # find the list of items in the original subreport
        old_employees = self.env['custom_reports.employee_performance'].search([
            ('employee_performance_report_id', '=', self.id)
        ])
        old_employees_ids = []
        for old_employee in old_employees:
            old_employees_ids.append(old_employee.employee_id.id)
        new_employees_ids = values['employee_ids'][0][2]
        remove_list = []
        add_records = []
        # if an old item is not in the new list, add item to the remove list
        for old_employee_id in old_employees_ids:
            if old_employee_id not in new_employees_ids:
                remove_list.append(old_employee_id)
        # if a new item is not in the old list, add item to the add list
        for new_employee_id in new_employees_ids:
            if new_employee_id not in old_employees_ids:
                add_records.append({
                    'employee_id': new_employee_id,
                    'employee_performance_report_id':  self.id,
                    'start_date': self.start_date,
                    'end_date': self.end_date
                })
        # remove items in the remove list from the subreport
        remove_records = self.env['custom_reports.employee_performance'].search([
            ('employee_id', 'in', remove_list)
        ])
        remove_records.unlink()
        # add items in the add list to the subreport
        self.env['custom_reports.employee_performance'].create(add_records)
        return record

    # check date validity (start date cannot be after end date)
    @api.constrains('start_date','end_date')
    def _check_date_validity(self):
        for report in self:
            if report.start_date and report.end_date:
                if report.start_date > report.end_date:
                    raise ValidationError(_("Error. Start date must be earlier than end date."))
    
#Employee Performance DataModel (Sub Report)
class EmployeePerformance(models.Model):
    _name = 'custom_reports.employee_performance'
    _description = 'Employee Performance'

    # properties
    employee_id = fields.Many2one('hr.employee', string="Employee", ondelete='cascade', index=True, store=True)
    employee_user_id = fields.Many2one(related='employee_id.user_id', store=True, readonly=True)
    employee_performance_report_id = fields.Many2one('custom_reports.employee_performance_report', string="Employee Performance Report", ondelete='cascade', store=True)
    start_date = fields.Datetime(related='employee_performance_report_id.start_date', required=True)
    end_date = fields.Datetime(related='employee_performance_report_id.end_date', required=True)

    # computed properties
    worked_hours = fields.Float(string="Worked Hours", compute="_compute_worked_hours", readonly=False)
    total_sales = fields.Float(string="Total Sales", compute="_compute_total_sales", readonly=False)
    sales_hour = fields.Float(string="Sales / Hour", compute="_compute_sales_hour", readonly=False)

    # methods
    # this method gets the computed work hours between a time period
    @api.depends('employee_id', 'start_date', 'end_date')
    def _compute_worked_hours(self):
        for record in self:
            worked_hours = 0.0           
            if record.employee_id and (record.start_date <= record.end_date):
                attendances = record.env['hr.attendance'].search([
                    ('employee_id', '=', record.employee_id.id),
                    ('check_in', '<=', record.end_date),
                    ('check_out', '>=', record.start_date)
                ])
                if attendances: # if found in attendance, sum the worked_hours
                    for attendance in attendances:
                        worked_hours += attendance.worked_hours
            record.worked_hours = worked_hours

    # this method gets the computed total sales between a time period
    @api.depends('employee_id', 'employee_user_id', 'start_date', 'end_date')
    def _compute_total_sales(self):
        for record in self:
            total_sales = 0.00
            if record.employee_id and (record.start_date <= record.end_date):
                orders = record.env['sale.order'].search([
                    ('state', 'in', ['sale', 'done']),
                    ('user_id', '=', record.employee_user_id.id),
                    ('date_order', '>=', record.start_date),
                    ('date_order', '<=', record.end_date)
                ])
                if orders: # if found in orders, sum the total sales
                    for sale in orders:
                        total_sales += sale.amount_total
            record.total_sales = total_sales
    
    # this method gets the computer sales per hour between a time period
    @api.depends('total_sales', 'worked_hours')
    def _compute_sales_hour(self):
        for record in self:
            if(record.worked_hours == 0 or record.total_sales == 0):
                record.sales_hour = 0
            else:
                record.sales_hour = record.total_sales / record.worked_hours
        