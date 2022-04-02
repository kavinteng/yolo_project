import cv2
import torch
import time
import numpy as np
import datetime
import csv
import shutil
import os
import requests, json
import sqlite3
from configparser import ConfigParser

model = torch.hub.load('ultralytics/yolov5', 'yolov5l', pretrained=True)
model.conf = 0.1
model.iou = 0.4

def build_folder_file():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    vdo_recode = os.path.join(base_dir,'record')
    backup_img = os.path.join(base_dir, "backup_file")
    date_img = os.path.join(backup_img, "{}".format(datetime.date.today()))
    try:
        os.mkdir(vdo_recode)
    except:
        pass
    try:
        os.mkdir(backup_img)
    except:
        pass
    try:
        os.mkdir(date_img)
    except:
        pass
    try:
        with open('backup_file/Head-count(not for open).csv') as f:
            pass
    except:
        header = ['File name','วัน', 'เวลา','จำนวนคนทั้งหมด', 'พนักงาน advice', 'ลูกค้า', 'จำนวนคนที่เดินผ่าน', 'POST STATUS']
        with open('backup_file/Head-count(not for open).csv', 'w', encoding='UTF-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
    try:
        with open('{}/landmark.csv'.format(date_img)) as f:
            pass
    except:
        header = ['Time','Xmin', 'Ymin', 'Xmax', 'Ymax']
        with open('{}/landmark.csv'.format(date_img), 'w', encoding='UTF-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)

    return date_img

def build_csv(data):
    try:
        with open('backup_file/Head-count(not for open).csv', 'a', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            # write multiple rows
            writer.writerows(data)
    except:
        print('File is open, Process will pause')
    try:
        shutil.copyfile('backup_file/Head-count(not for open).csv', 'result.csv')
    except:
        pass

def build_landmark(date_img, landmark):
    try:
        with open('{}/landmark.csv'.format(date_img), 'a', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            # write multiple rows
            writer.writerows(landmark)
    except:
        print('File is open, Process will pause')

def main(device_name,url=None,cap = 0,display_alltime=False,display_out = False,time_ref = 10,line_notify=5,polygon_employ=None,polygon_nodetect=None):
    dummy_start = None
    cap = cv2.VideoCapture(cap)

    check_rec = 0
    line_check = 0
    start = None
    check_best = False
    best_count = 0
    old = -1
    size_img_vdo = (640, 360)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    while True:
        try:
            repost_logfile(url)
        except:
            pass
        date_img = build_folder_file()
        output = []
        Date = datetime.datetime.now().strftime("%d/%m/%Y")
        Time = datetime.datetime.now().strftime("%T")

        if start == None:
            start = time.time()
        end = time.time()

        _,frame = cap.read()
        if frame is None:
            break
        if dummy_start == None:
            print('test dummy')
            dummy_start = model(frame, size=1)
            print('finish test')
            continue


        frame = cv2.resize(frame,size_img_vdo)

        image = frame.copy()
        img_record = frame.copy()

        if end - start > time_ref:
            real_check_out = True
            start = None
        else:
            real_check_out =False

        if (real_check_out == True) or (check_best == True):
            check_best = True
            employee = 0
            customer = 0
            walking_pass = 0
            results = model(frame, size=640)
            out2 = results.pandas().xyxy[0]

            if len(out2) != 0:
                for i in range(len(out2)):
                    output_landmark = []
                    xmin = int(out2.iat[i, 0])
                    ymin = int(out2.iat[i, 1])
                    xmax = int(out2.iat[i, 2])
                    ymax = int(out2.iat[i, 3])

                    cenx = (xmax + xmin) // 2
                    ceny = (ymax + ymin) // 2
                    conf = out2.iat[i, 4]
                    obj_name = out2.iat[i, 6]
                    if obj_name == 'person' or obj_name == '0':
                        x = xmax - xmin
                        y = ymax - ymin
                        dis = (x * y) / 100

                        xmin_new = xmin
                        ymin_new = ymin
                        xmax_new = xmax
                        ymax_new = int(ymin + (y/2))
                        if ymax_new > 360:
                            ymax_new = 360

                        # try:
                        #     shirt = image[ymin_new:ymax_new, xmin_new:xmax_new]
                        #     # lower1 = np.array([167, 111, 60])
                        #     # upper1 = np.array([170, 122, 101])
                        #     lower1 = np.array([28, 27, 58])
                        #     upper1 = np.array([71, 39, 255])
                        #     mask1 = cv2.inRange(shirt, lower1, upper1)
                        #
                        #     # lower2_1 = np.array([44, 29, 28])
                        #     # upper2_1 = np.array([47, 35, 28])
                        #     lower2_1 = np.array([27, 15, 10])
                        #     upper2_1 = np.array([29, 22, 45])
                        #     mask2_1 = cv2.inRange(shirt, lower2_1, upper2_1)
                        #
                        #     result_final2_1 = cv2.bitwise_or(mask2_1, mask1)
                        #
                        #     gray_thresh = cv2.adaptiveThreshold(result_final2_1, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                        #                                         cv2.THRESH_BINARY_INV, 11, 1)
                        #     kernel = np.ones((3,3), np.uint8)
                        #     closing = cv2.morphologyEx(gray_thresh,cv2.MORPH_CLOSE, kernel, iterations=5)
                        #     contours, hierachy = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        #     if contours == () or contours == []:
                        #         color = (255, 0, 0)
                        #     else:
                        #         array_area = []
                        #         for cnt in contours:
                        #             area = cv2.contourArea(cnt)
                        #             array_area.append(area)
                        #
                        #         out_sum = sum(array_area)
                        #         thresh = 200
                        #         if out_sum > thresh:
                        #             color = (0, 0, 255)
                        #         else:
                        #             color = (255, 0, 0)
                        # except:
                        #     color = (255, 0, 0)

                        output_landmark.append([Time,xmin,ymin,xmax,ymax])
                        build_landmark(date_img, output_landmark)

                        color = draw_polygon(cenx, ceny, polygon_nodetect, polygon_employ)

                        if color == (0, 0, 255):
                            employee += 1
                        elif color == (255, 0, 0):
                            customer += 1
                        elif color == (0, 255, 0):
                            walking_pass += 1
                        elif color == (0, 0, 0):
                            pass

                        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
                        # cv2.rectangle(frame, (xmin_new, ymin_new), (xmax_new, ymax_new), color, 2)
                        # cv2.putText(frame, 'Head: {:.2f}'.format(acc * 100), (xmin, ymin - 5),
                        #             cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 1)
                        cv2.rectangle(frame, (0, 0), (200,50), (255, 255, 255), -1)
                        cv2.putText(frame, 'Head Count:{}'.format(employee+customer+walking_pass), (10, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,
                                    (0, 0, 0),2)

                        # cv2.imshow('asd',frame)
                        # cv2.imshow('zxc',extracted)
                        # cv2.imshow('dsa',closing)
                        # cv2.waitKey(0)

            if best_count < 5:
                best_count += 1
                count_all = employee + customer + walking_pass
                if count_all > old:
                    old = count_all
                    store_frame = frame
                    store_emp = employee
                    store_cus = customer
                    store_walkpass = walking_pass

            else:
                best_count = 0
                old = -1
                check_best = False
                line_check += 1
                file_name = Time.replace(':', '-')
                # post json ----------------------------------------------

                count_all_json = store_emp + store_cus + store_walkpass
                file_json = file_name + '.jpg'
                dd,mm,yyyy = Date.split('/')
                date_json = f'{yyyy}-{mm}-{dd}'
                time_json = date_json + f' {Time}'

                text_for_post = {"people_device": device_name,"img_name": file_json,"img_date": date_json, "img_time": time_json,
                        "people_total": count_all_json, "people_advice": store_emp,
                        "people_other": store_cus, "storefront": store_walkpass}

                text = {"Status_post": 'Addlog'}

                try:
                    status_post = request_post(url,text_for_post)
                    if status_post == 0:
                        text['Status_post'] = 'No'
                        print(text_for_post, text)
                    elif status_post == 1:
                        text['Status_post'] = 'Yes'
                        print(text_for_post, text)
                    elif status_post == 2:
                        text['Status_post'] = 'empty url'
                        print(text_for_post, text)
                except:
                    print(text_for_post)
                    print('add to logfile')
                    addlog(device_name,file_json,date_json,time_json,count_all_json,store_emp,store_cus,store_walkpass)

                # --------------------------------------------------------
                status_post_csv = text['Status_post']
                output.append([file_json,Date,Time,count_all_json,store_emp,store_cus,store_walkpass,status_post_csv])

                img_file = date_img + '/' + file_name + '.jpg'
                cv2.imwrite(img_file,store_frame)
                if display_out:
                    cv2.imshow('frame{}'.format(Time),store_frame)
                build_csv(output)
                if line_check == line_notify and line_notify != False:
                    line_check = 0
                    try:
                        line_pic('{} {}'.format(Date,Time), img_file)
                    except:
                        print('No internet connection')

        if check_rec == 0:
            h, m, s = Time.split(':')
            time_record = '-' + str(h) + '-' + str(m) + '-' + str(s)
            file_record = 'record/' + str(datetime.date.today()) + time_record + '.mp4'
            rec = cv2.VideoWriter(file_record, fourcc, 25, size_img_vdo)
            check_rec = 1
        if check_rec == 1:
            rec.write(img_record)
            
        if display_alltime == True:
            cv2.imshow('frame',frame)
        k = cv2.waitKey(25)
        if k == ord('q'):
            break
    rec.release()
    cap.release()
    cv2.destroyAllWindows()

def line_pic(message, path_file):
    LINE_ACCESS_TOKEN = "US4BqFvpMcMoTDB4ea9l4bXeGdAA4quMkCzoIWy1Vrb"
    URL_LINE = "https://notify-api.line.me/api/notify"
    file_img = {'imageFile': open(path_file, 'rb')}
    msg = ({'message': message})
    LINE_HEADERS = {"Authorization": "Bearer " + LINE_ACCESS_TOKEN}
    session = requests.Session()
    session_post = session.post(URL_LINE, headers=LINE_HEADERS, files=file_img, data=msg)
    print(session_post.text)

def request_post(url, text):
    if url == None:
        status_post = 2
    else:
        response = requests.post(url, json=text)
        print('\n------posting------')
        if response.ok:
            print("Upload completed successfully!")
            status_post = 1

        else:
            print("Fall upload!")
            response.status_code
            status_post = 0

    return status_post

def create_logfile():
    con = sqlite3.connect('logfile.db')
    cur = con.cursor()
    cur.execute('''CREATE TABLE log
                   (people_device char(7), img_name char(15), img_date char(15), img_time char(15), 
                   people_total int, people_advice int, people_other int, storefront int)''')

    con.commit()
    con.close()

def addlog(device_name,file_json,date_json,time_json,count_all_json,store_emp,store_cus,store_walkpass):
    con = sqlite3.connect('logfile.db')
    cur = con.cursor()
    sql = '''INSERT INTO log(people_device, img_name, img_date, img_time,
                   people_total, people_advice, people_other) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
    task = (device_name,file_json,date_json,time_json,count_all_json,store_emp,store_cus,store_walkpass)
    cur.execute(sql, task)
    con.commit()
    con.close()

def repost_logfile(url):
    con = sqlite3.connect('logfile.db')
    cur = con.cursor()
    array = []
    for row in cur.execute('SELECT * FROM log'):
        device_name, file_json, date_json, time_json, count_all_json, store_emp, store_cus, store_walkpass = row
        array.append([device_name, file_json, date_json, time_json, count_all_json, store_emp, store_cus, store_walkpass])

    for row_store in array:
        text_for_post = {"people_device": row_store[0], "img_name": row_store[1], "img_date": row_store[2],
                         "img_time": row_store[3],"people_total": row_store[4], "people_advice": row_store[5],
                         "people_other": row_store[6],"storefront": row_store[7]}
        status_post = request_post(url, text_for_post)
        if status_post == 1:
            print(text_for_post)
            print('repost successfully')
            cur.execute("DELETE FROM log WHERE img_time=?",(row_store[3],))
            con.commit()

    con.close()

def set_polygon():
    global array1,array2, img
    # reading the image
    size_img_vdo = (640, 360)
    cap = cv2.VideoCapture(0)
    array1 = []
    array2 = []
    check_click = 0
    while True:
        _, img = cap.read()
        img = cv2.resize(img, size_img_vdo)

        # displaying the image
        # cv2.imshow('image', img)

        # cv2.setMouseCallback('image', click_event)
        # if len(array1) != 0:
        #     print(array1)
        if check_click == 2:
            contours1 = np.array(result1)
            contours2 = np.array(result2)
            cv2.fillPoly(img, pts=[contours2], color=(2, 255, 255))
            cv2.fillPoly(img, pts=[contours1], color=(1, 0, 255))
        # cv2.fillPoly(img, pts=[result3], color=(3, 0, 255))
        cv2.imshow('image', img)
        cv2.setMouseCallback('image', click_event)
        k = cv2.waitKey(0)
        if (k == 113) and (check_click ==3):
            break
        elif k == 100:
            print('clear array')
            array1 = []
            array2 = []
            check_click = 0
        elif (k == 122) and (check_click ==0):
            print('save array1')
            result1 = array1
            array1 = []
            array2 = []
            check_click += 1
        elif (k == 120) and (check_click ==1):
            print('save array2')
            result2 = array2
            array1 = []
            array2 = []
            check_click += 1
        elif (k == 99) and (check_click ==2):
            try:
                print(f'check array\n{result1}\n{result2}')
                check_click += 1
            except:
                print(f'Non save value: {array1}')
        else:
            pass
        # close the window
    cv2.destroyAllWindows()

    return result1, result2

def draw_polygon(cenx, ceny, polygon1, polygon2):
    contours1 = np.array(polygon1)
    contours2 = np.array(polygon2)
    array_miny = []
    for val in polygon1:
        array_miny.append(val[1])
    for val2 in polygon2:
        array_miny.append(val2[1])
    image = np.zeros((360, 640, 3))
    cv2.fillPoly(image, pts=[contours1], color=(2, 255, 255))
    cv2.fillPoly(image, pts=[contours2], color=(1, 0, 255))
    if int(image[ceny, cenx, 0]) == 1:
        color = (0, 0, 255)
    elif int(image[ceny, cenx, 0]) == 2:
        color = (255, 0, 0)
    elif ceny > min(array_miny):
        color = (0, 255, 0)
    else:
        color = (0, 0, 0)
    # cv2.imshow("filledPolygon", image)
    return color

def click_event(event, x, y, flags, params):
    global array1,array2, img
    if event == cv2.EVENT_LBUTTONDOWN:
        font = cv2.FONT_HERSHEY_SIMPLEX
        # print(x, ",", y)
        cv2.putText(img, str(x) + ',' +
                    str(y), (x, y), font,
                    1, (255, 0, 0), 2)
        array1.append([x, y])
        array2.append([x, y])
        cv2.imshow('image', img)

def write_polygon_value(polygon_employ,polygon_nodetect):
    write_config = ConfigParser()
    write_config.add_section('polygon')
    write_config.set('polygon', 'polygon_employ',str(polygon_employ))
    write_config.set('polygon', 'polygon_no_detect', str(polygon_nodetect))
    cfgfile = open('config.ini','w')
    write_config.write(cfgfile)
    cfgfile.close()

def read_polygon_value():
    read_config = ConfigParser()
    read_config.read('config.ini')
    polygon_employ = read_config.get('polygon','polygon_employ')
    polygon_nodetect = read_config.get('polygon', 'polygon_no_detect')
    polygon_employ = json.loads(polygon_employ)
    polygon_nodetect = json.loads(polygon_nodetect)
    return polygon_employ,polygon_nodetect
# def read_db():
#     con = sqlite3.connect('logfile.db')
#     cur = con.cursor()
#     array = []
#     for row in cur.execute('SELECT * FROM log'):
#         print(row)
#         device_name,file_json,date_json,time_json,count_all_json,store_emp,store_cus = row
#         print(time_json)
#         array.append(time_json)
#         # cur.execute('''DELETE FROM log WHERE img_time=?''', (time_json,))
#         # print('delete')
#     print(array)
#     for time_array in array:
#         cur.execute('''DELETE FROM log WHERE img_time=?''', (time_array,))
#         print('delete')
#     con.commit()
#     con.close()
# if __name__ == '__main__':
#     read_db()
#     repost_logfile()