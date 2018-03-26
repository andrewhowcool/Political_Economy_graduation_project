import requests
import pandas as pd
import multiprocessing as mp
from functools import partial

url = 'http://mops.twse.com.tw/mops/web/ajax_t163sb04'
head = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}
payload = {
    'encodeURIComponent':'1',
    'step':'1',
    'firstin':'1',
    'off':'1',
    'TYPEK':'sii',
    'year':'',
    'season':''
}


def inputs(raw):

    y_start = int(raw[0])
    y_end = int(raw[2])
    s_start = int(raw[1])
    s_end = int(raw[3])
    
    outputs = []
    
    #跨年度
    if y_end - y_start == 1:
        
        #start
        s = 4 - s_start + 1
        for i in range(s):
            outputs.append([y_start, s_start])
            s_start += 1
            
        #end
        s = 1
        for i in range(s_end):
            outputs.append([y_end, s])
            s += 1      
        
        return outputs
    
    #同年度
    elif y_end == y_start:
        s = s_end - s_start + 1
        for i in range(s):
            outputs.append([y_start, s_start])
            s_start += 1
            
        return outputs
    
    
def elec(raw):
    
    #電子類股：公司代號
    #資料來源:GoodInfo  https://goodinfo.tw/StockInfo/StockList.asp?MARKET_CAT=全部&INDUSTRY_CAT=電子零組件業&SHEET=交易狀況&SHEET2=日&RPT_TIME=最新資料
    elec_companies = [
        #電子零組件
            1471,	    1582,	    2059,	    2308,	    2313,	    2316,	    2327,	    2328,	    2355,	    2367,	    2368,	    2375,	    2383,	    2385,	    2392,	    2402,	    2413,	    2415,	    2420,	    2421,	    2428,	    2429,	    2431,	    2440,	    2443,	    2456,	    2457,	    2460,	    2462,	    2467,	    2472,	    2476,	    2478,	    2483,	    2484,	    2492,	    2493,	    3003,	    3011,	    3015,	    3021,	    3023,	    3026,	    3032,	    3037,	    3042,	    3044,	    3058,	    3090,	    3229,	    3296,	    3308,	    3321,	    3338,	    3376,	    3432,	    3501,	    3533,	    3550,	    3593,	    3605,	    3607,	    3645,	    3653,	    3679,	    4545,	    4912,	    4915,	    4927,	    4943,	    4958,	    4999,	    5469,	    6108,	    6115,	    6133,	    6141,	    6153,	    6155,	    6165,	    6191,	    6197,	    6205,	    6213,	    6224,	    6251,	    6269,	    6282,	    6412,	    6422,	    6449,	    8039,	    8046,	    8103,	    8213,	    8249,	    1503,
        #電機機械
            1504,	1506,	1507,	1512,	1513,	1514,	1515,	1517,	1519,	1521,	1522,	1524,	1525,	1526,	1527,	1528,	1529,	1530,	1531,	1532,	1533,	1535,	1536,	1537,	1538,	1539,	1540,	1541,	1558,	1560,	1566,	1568,	1570,	1580,	1583,	1586,	1589,	1590,	1591,	1592,	1597,	1599,	2049,	2066,	2067,	2228,	2230,	2231,	2233,	2235,	2236,	2371,	3162,	3167,	3226,	3379,	3426,	4502,	4503,	4506,	4510,	4513,	4523,	4526,	4527,	4528,	4530,	4532,	4533,	4534,	4535,	4543,	4549,	4550,	4551,	4552,	4555,	4557,	4560,	4562,	5288,	6122,	6603,	6605,	6609,	8027,	8083,	8107,	8222,	8255,	8374,	8996,	9951,
        #電器電纜
            1603,	1604,	1605,	1608,	1609,	1611,	1612,	1614,	1615,	1616,	1617,	1618,	1626,	2061,	4609,	4930,
        #電腦及週邊
            1569,	2301,	2305,	2324,	2331,	2352,	2353,	2356,	2357,	2362,	2364,	2365,	2376,	2377,	2380,	2382,	2387,	2395,	2397,	2399,	2405,	2417,	2424,	2425,	2442,	2465,	3002,	3005,	3013,	3017,	3022,	3046,	3057,	3060,	3071,	3088,	3211,	3213,	3231,	3272,	3287,	3323,	3325,	3416,	3479,	3483,	3494,	3515,	3521,	3540,	3577,	3594,	3611,	3625,	3652,	3693,	3701,	3706,	4916,	4924,	4938,	4987,	5215,	5258,	5264,	5289,	5304,	5356,	5386,	5426,	5438,	5450,	5465,	5474,	5490,	6105,	6117,	6121,	6123,	6128,	6150,	6160,	6161,	6166,	6172,	6188,	6206,	6222,	6228,	6230,	6235,	6276,	6277,	6298,	6414,	6577,	6579,	8050,	8076,	8114,	8163,	8210,	8234,	8299,	8410,	9912,
        #半導體
            1437,	2302,	2303,	2311,	2325,	2329,	2330,	2337,	2338,	2342,	2344,	2351,	2363,	2369,	2379,	2388,	2401,	2408,	2434,	2436,	2441,	2449,	2451,	2454,	2458,	2481,	3006,	3014,	3016,	3034,	3035,	3041,	3054,	3073,	3094,	3105,	3122,	3141,	3169,	3188,	3189,	3227,	3228,	3257,	3259,	3260,	3264,	3265,	3268,	3317,	3372,	3374,	3413,	3438,	3443,	3519,	3527,	3529,	3532,	3536,	3545,	3553,	3555,	3556,	3567,	3579,	3581,	3583,	3588,	3661,	3675,	3680,	3686,	3707,	4919,	4947,	4952,	4966,	4968,	4971,	4973,	4991,	5269,	5272,	5274,	5285,	5302,	5305,	5314,	5344,	5347,	5351,	5425,	5455,	5468,	5471,	5483,	5487,	6103,	6104,	6129,	6138,	6147,	6182,	6198,	6202,	6223,	6229,	6233,	6237,	6239,	6243,	6257,	6261,	6271,	6287,	6291,	6411,	6415,	6435,	6451,	6457,	6462,	6485,	6488,	6494,	6510,	6525,	6531,	6532,	6533,	6552,	6568,	6594,	8016,	8024,	8040,	8054,	8081,	8086,	8088,	8110,	8131,	8150,	8261,	8271,	8277,
        #其他電子業
            1785,	2312,	2317,	2354,	2359,	2360,	2390,	2404,	2423,	2433,	2461,	2464,	2474,	2477,	2482,	2488,	2495,	2497,	3018,	3030,	3043,	3064,	3067,	3093,	3131,	3285,	3289,	3305,	3324,	3373,	3402,	3450,	3498,	3508,	3518,	3541,	3551,	3552,	3563,	3580,	3587,	3617,	3628,	3642,	3663,	3665,	4554,	5225,	5383,	5452,	5489,	5493,	5536,	6139,	6144,	6146,	6151,	6187,	6196,	6201,	6215,	6238,	6247,	6275,	6409,	6438,	6512,	8021,	8047,	8085,	8092,	8183,	8201,	8383,	8431,	8455,
        #光電業
            2323,	2340,	2349,	2374,	2393,	2406,	2409,	2426,	2438,	2448,	2466,	2475,	2486,	2489,	2491,	2499,	3008,	3019,	3024,	3031,	3038,	3049,	3050,	3051,	3059,	3066,	3128,	3149,	3230,	3297,	3339,	3356,	3362,	3383,	3406,	3428,	3434,	3437,	3441,	3452,	3454,	3455,	3481,	3490,	3504,	3514,	3516,	3522,	3523,	3531,	3535,	3557,	3561,	3562,	3576,	3591,	3615,	3622,	3623,	3629,	3630,	3666,	3669,	3673,	3685,	3691,	3698,	4729,	4933,	4934,	4935,	4942,	4944,	4956,	4960,	4972,	4976,	4995,	5230,	5234,	5243,	5245,	5251,	5259,	5281,	5315,	5371,	5392,	5432,	5443,	5484,	6116,	6120,	6125,	6131,	6164,	6167,	6168,	6176,	6209,	6225,	6226,	6234,	6244,	6246,	6278,	6289,	6405,	6419,	6431,	6443,	6456,	6477,	6548,	6560,	7402,	8049,	8064,	8069,	8087,	8105,	8111,	8215,	8240,
        #通訊網路
            2314,	2321,	2332,	2345,	2412,	2419,	2439,	2444,	2450,	2455,	2485,	2496,	2498,	3025,	3027,	3045,	3047,	3062,	3068,	3081,	3095,	3152,	3163,	3221,	3234,	3290,	3299,	3306,	3311,	3363,	3380,	3419,	3431,	3466,	3491,	3499,	3558,	3564,	3596,	3632,	3664,	3672,	3682,	3684,	3694,	3704,	4903,	4904,	4905,	4906,	4908,	4909,	4977,	4979,	4984,	5348,	5353,	5388,	6109,	6136,	6142,	6143,	6152,	6163,	6170,	6190,	6216,	6218,	6241,	6245,	6263,	6283,	6285,	6417,	6426,	6442,	6465,	6470,	6486,	6514,	8011,	8034,	8048,	8059,	8097,	8101,	8171,	8176,
        #資訊服務
            2427,	2453,	2468,	2471,	3029,	3083,	3085,	3130,	3293,	3546,	3570,	3687,	4946,	4953,	4965,	4994,	5201,	5202,	5203,	5205,	5209,	5210,	5211,	5212,	5278,	5287,	5310,	5403,	5410,	5478,	6111,	6112,	6140,	6148,	6169,	6180,	6183,	6214,	6221,	6231,	6240,	6404,	8044,	8099,	8416,	8472,	8477,
        #電子通路
            2347,	2414,	2430,	2459,	3010,	3028,	3033,	3036,	3048,	3055,	3209,	3224,	3232,	3312,	3315,	3360,	3444,	3528,	3702,	5434,	6107,	6113,	6118,	6145,	6154,	6189,	6227,	6265,	6270,	6281,	8032,	8067,	8068,	8070,	8084,	8096,	8112
    ]    
    
    for i in range(len(elec_companies)):
        elec_companies[i] = str(elec_companies[i])
        
    table = raw[raw[0].isin(elec_companies)]
    
    return table


def compare_year(year1, year2):
    
    #取出表格的公司代號欄，轉換成set
    code1 = set(year1[0])
    code2 = set(year2[0])
       
    #取兩年度公司代號之交集
    code = code1.intersection(code2)
    code = list(code)
    
    #year1
    table1 = year1[year1[0].isin(code)]
    table1 = table1.reset_index(drop=True) #重設index  
    

    #year2
    table2 = year2[year2[0].isin(code)]
    table2 = table2.reset_index(drop=True) #重設index  
    
    
    return(table1, table2)


def compare_season(raw, s):
    if s == 3:
        s1 = raw[0]
        s2 = raw[1]
        s3 = raw[2]
        
        #取出表格的公司代號欄，轉換成set
        code1 = set(s1['公司代號'])
        code2 = set(s2['公司代號'])
        code3 = set(s3['公司代號'])

        #取三季度公司代號之交集
        code = code1.intersection(code2, code3)
        code = list(code)   

        #s1
        table1 = s1[s1['公司代號'].isin(code)]
        table1 = table1.reset_index(drop=True) #重設index      

        #s2
        table2 = s2[s2['公司代號'].isin(code)]
        table2 = table2.reset_index(drop=True) #重設index  

        #s3
        table3 = s3[s3['公司代號'].isin(code)]
        table3 = table3.reset_index(drop=True) #重設index 

        return(table1, table2, table3)
          


def category(raw):
    
    series = raw[0:1]
    category1 = [] #儲存公司代號、公司名稱、營業收入、營業毛利、基本每股盈餘之index
    category2 = [] #儲存所有類別的index
    
    for i in series:
        category2.append(series[i].name)
        if series[i][0] == '公司代號' or series[i][0] == '公司名稱' or series[i][0] == '營業收入' or series[i][0] == '營業毛利（毛損）淨額' or series[i][0] == '基本每股盈餘（元）':
            category1.append(i)    
    
    category1 = set(category1) #轉成set
    category2 = set(category2) #轉成set
    category3 = list(category2 - category1) #category3為不要的類別
    
    table = raw.drop(category3, axis=1)#刪除不要的類別  
    table.columns = [0, 1, 2, 3, 4]#重設column index    
    
    return table


def season(year):
    
    payload['year'] = year[0]    
    payload['season'] = year[1]  
    
    req = requests.post(url, data = payload, headers = head)
    req.encoding = 'utf8'
    
    table = pd.read_html(req.text)[3] #第四張表格才是我們要的資料   
    table = category(table)#篩選出eps, 營收, 毛利
    table = elec(table)#刪除非電子零件類股    
        
    return table


def growth(year):#y1新, y2舊

    #從year取出兩個年度
    year1 = year[0]
    year2 = year[1]
    
    #使y1, y2 公司名單相同
    y = compare_year(year1, year2)
    y1 = y[0]
    y2 = y[1]

    code = []#公司代號
    company = []#公司名稱
    income = []#營業收入
    profit = []#營業毛利（毛損）淨額
    eps = []#基本每股盈餘（元）

    for j in range(1, y1.shape[0]):
        code.append(y1[0][j])
        company.append(y1[1][j])
        income.append((float(y1[2][j]) - float(y2[2][j])) / float(y2[2][j]))#income成長率
        profit.append((float(y1[3][j]) - float(y2[3][j])) / float(y2[3][j]))#profit成長率

        #萬一eps為零，為了不讓分母為零，將其設為0.00000000000000000001
        if float(y2[4][j]) == 0:
            y2[4][j] = 0.00000000000000000001
        
        #分母必須為正，否則成長率有時會正負相反
        mother = float(y2[4][j])
        if mother < 0:
            mother = mother*(-1)
        eps.append((float(y1[4][j]) - float(y2[4][j])) / mother)#eps成長率

    s = {
        '公司代號':code,
        '公司名稱':company,
        '營業收入':income,
        '營業毛利（毛損）淨額':profit,
        '基本每股盈餘（元）':eps
    }
    s = pd.DataFrame(data = s)
        
    return s

#     return (year1, year2, y1, y2)


def multicore_season(y, pool):

    res = pool.map(season, y)#迭代相對應的次數
    
    return res


def multicore_growth(s, y_new, y_old, pool):
    
    y_new = multicore_season(y_new, pool)
    y_old = multicore_season(y_old, pool)    
    
    y = []
    for i in range(s):
        y.append([y_new[i], y_old[i]])

    res = pool.map(growth, y)
    
    return res


def eps(t, s):
    #3季
    if s == 3:
        t1 = t[0]
        t2 = t[1]
        t3 = t[2]
        
        #只留下eps欄
        t1 = t1.drop(['營業收入', '營業毛利（毛損）淨額'], axis=1)
        t2 = t2.drop(['營業收入', '營業毛利（毛損）淨額'], axis=1)
        t3 = t3.drop(['營業收入', '營業毛利（毛損）淨額'], axis=1)
        
        #重設column index
        t1.columns = ['公司代號', '公司名稱', '基本每股盈餘']
        t2.columns = ['公司代號', '公司名稱', '基本每股盈餘']
        t3.columns = ['公司代號', '公司名稱', '基本每股盈餘']

        #使三季公司名單相同
        t = [t1, t2, t3]
        s = compare_season(t, s)
        s1 = s[0]
        s2 = s[1]
        s3 = s[2]

        for i in range(s1.shape[0]):
            if s1['基本每股盈餘'][i] <= 0 or s2['基本每股盈餘'][i] <= 0 or s3['基本每股盈餘'][i] <= 0: 
                s1 = s1.drop([i], axis = 0)
                s2 = s2.drop([i], axis = 0)
                s3 = s3.drop([i], axis = 0)

        #排序
        s1 = s1.sort_values(by = '基本每股盈餘', ascending = False)
        s2 = s2.sort_values(by = '基本每股盈餘', ascending = False)
        s3 = s3.sort_values(by = '基本每股盈餘', ascending = False)
        
        #重設index
        s1 = s1.reset_index(drop=True) 
        s2 = s2.reset_index(drop=True) 
        s3 = s3.reset_index(drop=True)         

        return (s1, s2, s3) 
    


def income(t, s):
    
    #3季
    if s == 3:
        t1 = t[0]
        t2 = t[1]
        t3 = t[2]
        
        #只留下eps欄
        t1 = t1.drop(['基本每股盈餘（元）', '營業毛利（毛損）淨額'], axis=1)
        t2 = t2.drop(['基本每股盈餘（元）', '營業毛利（毛損）淨額'], axis=1)
        t3 = t3.drop(['基本每股盈餘（元）', '營業毛利（毛損）淨額'], axis=1)
        
        #重設column index
        t1.columns = ['公司代號', '公司名稱', '營業收入']
        t2.columns = ['公司代號', '公司名稱', '營業收入']
        t3.columns = ['公司代號', '公司名稱', '營業收入']

        #使三季公司名單相同
        t = [t1, t2, t3]
        s = compare_season(t, s)
        s1 = s[0]
        s2 = s[1]
        s3 = s[2]

        for i in range(s1.shape[0]):
            if s1['營業收入'][i] <= 0 or s2['營業收入'][i] <= 0 or s3['營業收入'][i] <= 0: 
                s1 = s1.drop([i], axis = 0)
                s2 = s2.drop([i], axis = 0)
                s3 = s3.drop([i], axis = 0)

        #排序
        s1 = s1.sort_values(by = '營業收入', ascending = False)
        s2 = s2.sort_values(by = '營業收入', ascending = False)
        s3 = s3.sort_values(by = '營業收入', ascending = False)
        
        #重設index
        s1 = s1.reset_index(drop=True) 
        s2 = s2.reset_index(drop=True) 
        s3 = s3.reset_index(drop=True)         

        return (s1, s2, s3) 
    
    


def profit(t, s):
    #3季
    if s == 3:
        t1 = t[0]
        t2 = t[1]
        t3 = t[2]
        
        #只留下eps欄
        t1 = t1.drop(['基本每股盈餘（元）', '營業收入'], axis=1)
        t2 = t2.drop(['基本每股盈餘（元）', '營業收入'], axis=1)
        t3 = t3.drop(['基本每股盈餘（元）', '營業收入'], axis=1)
        
        #重設column index
        t1.columns = ['公司代號', '公司名稱', '營業毛利（毛損）淨額']
        t2.columns = ['公司代號', '公司名稱', '營業毛利（毛損）淨額']
        t3.columns = ['公司代號', '公司名稱', '營業毛利（毛損）淨額']

        #使三季公司名單相同
        t = [t1, t2, t3]
        s = compare_season(t, s)
        s1 = s[0]
        s2 = s[1]
        s3 = s[2]

        for i in range(1, s1.shape[0]):
            if s1['營業毛利（毛損）淨額'][i] <= 0 or s2['營業毛利（毛損）淨額'][i] <= 0 or s3['營業毛利（毛損）淨額'][i] <= 0: 
                s1 = s1.drop([i], axis = 0)
                s2 = s2.drop([i], axis = 0)
                s3 = s3.drop([i], axis = 0)

        #排序
        s1 = s1.sort_values(by = '營業毛利（毛損）淨額', ascending = False)
        s2 = s2.sort_values(by = '營業毛利（毛損）淨額', ascending = False)
        s3 = s3.sort_values(by = '營業毛利（毛損）淨額', ascending = False)
        
        #重設index
        s1 = s1.reset_index(drop=True) 
        s2 = s2.reset_index(drop=True) 
        s3 = s3.reset_index(drop=True)         

        return (s1, s2, s3) 
    



def intersection(e_raw, i_raw, p_raw):
    
    e1_raw = e_raw[0]
    i1_raw = i_raw[0]
    p1_raw = p_raw[0]
    
    e2_raw = e_raw[1]
    i2_raw = i_raw[1]
    p2_raw = p_raw[1]
    
    e3_raw = e_raw[2]
    i3_raw = i_raw[2]
    p3_raw = p_raw[2]
    
    #eps, income, profit皆有上榜才能留下，取其公司代號之交集
    e_code = set(e1_raw['公司代號'])
    i_code = set(i1_raw['公司代號'])
    p_code = set(p1_raw['公司代號'])
    code = e_code.intersection(i_code, p_code) #公司代號之交集
    code = list(code)  
    
    
    #重篩表格，把符合code的留下
    #eps
    e1_new = e1_raw[e1_raw['公司代號'].isin(code)]
    e1_new = e1_new.reset_index(drop=True) #重設index 
    
    e2_new = e2_raw[e2_raw['公司代號'].isin(code)]
    e2_new = e2_new.reset_index(drop=True) #重設index 
    
    e3_new = e3_raw[e3_raw['公司代號'].isin(code)]
    e3_new = e3_new.reset_index(drop=True) #重設index
    
    e_new = [e1_new, e2_new, e3_new]
    
    #income
    i1_new = i1_raw[i1_raw['公司代號'].isin(code)]
    i1_new = i1_new.reset_index(drop=True) #重設index 
    
    i2_new = i2_raw[i2_raw['公司代號'].isin(code)]
    i2_new = i2_new.reset_index(drop=True) #重設index 
    
    i3_new = i3_raw[i3_raw['公司代號'].isin(code)]
    i3_new = i3_new.reset_index(drop=True) #重設index
    
    i_new = [i1_new, i2_new, i3_new]
    
    #profit
    p1_new = p1_raw[p1_raw['公司代號'].isin(code)]
    p1_new = p1_new.reset_index(drop=True) #重設index 
    
    p2_new = p2_raw[p2_raw['公司代號'].isin(code)]
    p2_new = p2_new.reset_index(drop=True) #重設index 
    
    p3_new = p3_raw[p3_raw['公司代號'].isin(code)]
    p3_new = p3_new.reset_index(drop=True) #重設index
    
    p_new = [p1_new, p2_new, p3_new]    

    return (e_new, i_new, p_new)


def excel(eps, income, profit, s):
    #eps
    writer = pd.ExcelWriter('Eps.xlsx')
    eps[0].to_excel(writer,'season1')
    eps[1].to_excel(writer,'season2')
    if s > 2:
        eps[2].to_excel(writer,'season3')
    writer.save()
    
    #income
    writer = pd.ExcelWriter('Income.xlsx')
    income[0].to_excel(writer,'season1')
    income[1].to_excel(writer,'season2')
    if s > 2:
        income[2].to_excel(writer,'season3')
    writer.save()
    
    #profit
    writer = pd.ExcelWriter('Profit.xlsx')
    profit[0].to_excel(writer,'season1')
    profit[1].to_excel(writer,'season2')
    if s > 2:
        profit[2].to_excel(writer,'season3')
    writer.save()