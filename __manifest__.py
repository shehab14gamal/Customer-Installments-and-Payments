{
    'name': "customer_installments_and_payments",
    'version': '15',
    'description': 'odoo module which handles customer installments and payments.',
    'author': "my company",
    'depends': ['hr','account','account_accountant'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/installment_views.xml',

    ]


}