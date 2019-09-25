import csv
import numpy as np
import serial
import os
import ast

def startCollecting(num_classes = 4, data_num = 4, time = 5, how_many = 50):
    global data, data_gt, shuffle_map, test_begin_idx, output_cnt
    class_num = 0
    cnt = 0
    os.system('say hello everyone nice to meet you')
    data_gt = np.zeros(num_classes*how_many*time,)
    if os.path.exists('./beacon_data.csv') :
        print('file exists. Loading...')
        data = []
        with open('./beacon_data.csv') as csvfile:
            csvreader = csv.reader(csvfile)
            cnt = 0
            for row in csvreader:
                data_gt[cnt] = int(float(row[0]))
                row[1] = row[1].replace(' \n', ',').replace('      ',',').replace('     ',',').replace('    ',',').replace('   ',',').replace('  ',',').replace(' ', ',')
                row[1] = ast.literal_eval(row[1])
                data.append(row[1])
                cnt += 1
        data = np.array(data)
        print('loading complete')
    else:
        print('collecting data from serial...')
        data = np.zeros([num_classes*how_many, time, data_num])
        n_c=0
        n_h=0
        t=0
        with open('./beacon_data.csv', 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            for n_c in range(num_classes): #4
                print('collecting data for class {}'.format(n_c))
                print('loading bar:', end='')
                [print('*'*i, end='') for i in range(5)]
                for n_h in range(how_many): #50
                    data_gt[n_c + n_h] = n_c
                    for t in range(time): #5
                        tmp = start_serial()
                        print(tmp)
                        tmp = np.fromstring(tmp, dtype=float, sep=",")
                        print(tmp)
                        data[n_c + n_h][t] = tmp #size = (data_num,)
                    csvwriter.writerow([data_gt[n_c + n_h],data[n_c + n_h]])
        print('collecting completed')
    

    return data, data_gt
def arrange_data(mb_size=1):
    #shuffles data and returns step count -> used for test idx
    #mb = minibatch size
    global data, shuffle_map, test_begin_idx, output_cnt
    shuffle_map = np.arange(data.shape[0])
    np.random.shuffle(shuffle_map)
    step_count = int(data.shape[0] * 0.8) // mb_size
    test_begin_idx = step_count * mb_size
    return step_count

def get_test_data():
    global data, shuffle_map, test_begin_idx, output_cnt
    test_data = data[shuffle_map[test_begin_idx:]]
    test_data_gt = data_gt[shuffle_map[test_begin_idx:]]
    return test_data, test_data_gt

def get_train_data(mb_size=1):
    #if nth == 0:
        #np.random.shuffle(shuffle_map[:test_begin_idx])
    #train_data = data[shuffle_map[mb_size*nth:mb_size*(nth+1)]]
    train_data = data[shuffle_map[:test_begin_idx]]
    train_data_gt = data_gt[shuffle_map[:test_begin_idx]]
    return train_data, train_data_gt

def start_serial():
    with serial.Serial('/dev/ttyACM0', 9600) as ser:
        print(ser.readline())
        return ser.readline()
    
  