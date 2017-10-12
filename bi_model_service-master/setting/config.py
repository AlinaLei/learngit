MYSQL_BI_RW_ENV = 'bi_wr_RP'
MYSQLs_BI_RW_ENV = 'bi_r'
MYSQL_PRODUCT_R_ENV = 'p_bi_ro'

AccessKey_dict = {
    'lnyp': {
        'ho': "192.23.127.31,16188"
        , 'us': "vpclublnyp_read"
        , 'pwd': "PYT!#661jksw#REWlnyp"
        , 'db': "vpclubcloud"}
    , 'bi_wr': {
        'ho': 'rds317hdyffrhl07yopq.mysql.rds.aliyuncs.com'
        , 'us': "XXXXXXXXX"
        , 'pwd': "XXXXXXXXX"
        , 'db': "dw"}
    ,'bi_wr_RP': {
        'ho': '120.25.202.206'
        , 'us': "XXXXXXXXX"
        , 'pwd': "XXXXXXXXX"
        , 'pt': 20806
        , 'db': "bimodels"}
    , 'bi_r': {
        'ho': 'rr-wz9e478v8ba5737l8.mysql.rds.aliyuncs.com'
        , 'us': "XXXXXXXXX"
        , 'pwd': "XXXXXXXXX"
        , 'db': "dw"}
    , 'p_bi_r': {
        'ho': "rr-wz97k3w4o9hv1t82q.mysql.rds.aliyuncs.com"
        , 'us': "XXXXXXXXX"
        , 'pwd': "XXXXXXXXX"
        , 'db': "weicheche"}
    , 'p_bi_ro': {
        'ho': "rr-wz97k3w4o9hv1t82qo.mysql.rds.aliyuncs.com"
        , 'us': "XXXXXXXXX"
        , 'pwd': "XXXXXXXXX"
        , 'db': "weicheche"}}


WBASE = {
    'WEBserver': '120.77.65.191'
    , 'LOCAL_AREA_IP': '0.0.0.0'
    , 'FILE_PORT': '3333'
    , 'DOWNLOAD_PORT': '3334'
    , 'WEB_PORT': '8088'}