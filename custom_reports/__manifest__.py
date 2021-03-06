# -*- coding: utf-8 -*-
{
    'name': "Custom Reports",

    'summary': "Custom Reports",
    'description': """
        ClickIt COMP 4882 Custom Reports
    """,

    'version': '0.1',
    'depends': ['base', 'hr', 'hr_attendance', 'mass_mailing', 'product', 'point_of_sale', 'purchase', 'sale', 'sale_management', 'stock', 'web'],
    
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/sales_by_company_reports_views.xml',
        'views/employee_performance_reports_views.xml',
        'views/email_marketing_reports_views.xml',
        'views/contact_report_view.xml',
        'views/sales_statistics_reports_views.xml',
        'views/traffic_statistics_reports_views.xml',
        'views/restock_report_view.xml',
        'views/custom_reports_views.xml',
    ],
    'demo': [
        'demo/custom_report_demo.xml',
        'demo/employee_performance_demo.xml',
        'demo/email_marketing_demo.xml',
        'demo/sales_by_company_demo.xml',
        'demo/traffic_statistic_demo.xml'
        
    ],
    'qweb': [
        'static/src/xml/employee_performance_graph.xml',
        'static/src/xml/email_marketing_graph.xml',
        'static/src/xml/sales_by_company_graph.xml',
        'static/src/xml/sales_statistic_graph.xml',
        'static/src/xml/traffic_statistic_graph.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': True
}