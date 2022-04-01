from module import *

list_url = [None,
            'http://127.0.0.1:5000/count_person',
            'https://globalapi.advice.co.th/api/upload_people',
            'http://ec2-44-201-34-174.compute-1.amazonaws.com/count_person']
list_cap = [0,1,'Commart1.mp4','Commart2.mp4','ROB09760.jpg']
device_name = 'device1'

if os.path.isfile('logfile.db') == False:
    create_logfile()

if os.path.isfile('config.ini') == False:
    polygon_employ,polygon_nodetect = set_polygon()
    write_polygon_value(polygon_employ,polygon_nodetect)

polygon_employ, polygon_nodetect = read_polygon_value()
main(device_name,url=list_url[0], cap=list_cap[0],
     display_alltime=True, display_out=False,
     time_ref=10, line_notify=60,
     polygon_employ=polygon_employ,polygon_nodetect=polygon_nodetect)