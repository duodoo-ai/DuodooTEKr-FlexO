{
    'name': "Base Module(RTX)",
    'author': "Jason Zou",
    "website": "-",
    'summary': '隐藏内置技术复杂性，增加基本权限组',
    'category': '中国化应用/应用核心模块',
    "description":
    '''
    该模块是业务核心模块，完成了基本表的定义和配置。
    
    定义了基本配置： 用户、类别等；
    定义了高级配置： 系统参数、定价策略。
    
    更多支持：
    18951631470
    zou.jason@qq.com
    ''',
    'version': '1.0',
    'depends': ['web',
                'mail',
                'base',
                ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/server_log_views.xml',
        'views/core_clean_data_view.xml',
        'views/menu_views.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    "license": "AGPL-3",
}
