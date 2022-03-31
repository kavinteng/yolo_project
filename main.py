from module import *

list_url = [None,
            'http://127.0.0.1:5000/count_person',
            'https://globalapi.advice.co.th/api/upload_people',
            'http://ec2-44-201-34-174.compute-1.amazonaws.com/count_person']
list_cap = [0,1,'Commart1.mp4','Commart2.mp4','ROB09760.jpg']
main(url=list_url[0], cap=list_cap[1], display_alltime=True, display_out=False, time_ref=10, line_notify=60)