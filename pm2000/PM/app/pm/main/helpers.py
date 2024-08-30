from datetime import datetime








def test_ne(d1,d2,mess):

    not_equal=True
    
    try:
        if d2==d1:
            mess=''
    
    except:
        pass
        
    return mess





def test_date_ne(d1,d2,mess):

    try:
    
        if type(d1) is  datetime:
            d1=d1.date()
            
        if type(d2) is  datetime:
            d2=d2.date()
            
        if d2==d1:
            mess=''
    
    except:
        pass
        
    return mess



