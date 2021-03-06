#!/usr/bin/env python3
import sys 
import csv
import datetime
import getopt
import configparser


from multiprocessing import Process ,Queue,Pipe
global queue1,queue2
queue1 = Queue()
queue2 = Queue()
class Args(object):
    def __init__(self):
        self.args = sys.argv[1:]
        
    def read_fileroad(self):
        #index0 = self.args.index('-c')+1
        #index1 = self.args.index('-d')+1
        #index2 = self.args.index('-o')+1
        #return([self.args[index0],self.args[index1],self.args[index2]])
        opts,args = getopt.getopt(sys.argv[1:],"C:c:d:o:",['cityname','configfile','userdata','resultdata'])
        #return opts
        print(opts)
        opt_dict = {}
        for opt in opts:
            if opt[0] =='-C':
                opt_dict["cityname"] = opt[1]
            if opt[0] =='-c':
                opt_dict['configfile'] = opt[1]
            if opt[0] == '-d':
                opt_dict['userdata'] = opt[1]
            if opt[0]=='-o':
                opt_dict['resultdata'] = opt[1]
        return opt_dict


        


class IncomeTaxCalculator(object):
    def read_users_data(self,userfile):
        data = []
        with open(userfile,'r') as file:
            for line in file:
                l = line.strip().split(',')
                data.append(l)
        queue1.put(data)
        print(queue1)
        #return data

    def calc_for_all_userdata(self):
   
        Arg = Args()
        file_road = Arg.read_fileroad()
        cfg_file = file_road['configfile']
        conf = configparser.ConfigParser()
        conf.read(cfg_file)
        
        cityname = file_road.get('cityname')
        if cityname == None:
            config = dict(conf.items('DEFAULT'))
        else:
            config = dict(conf.items(cityname.upper()))
        
        print(config)
        user_file = file_road['userdata']
        #config = Config(cfg_file).config
        #userdata = self.read_users_data(user_file)
        userdata = queue1.get(timeout = 1)
        start_point= 3500
        try:
            all_user_output = []
            for items in userdata:
                key = int(items[0])
                value = int(items[1])
                insurance_prob = 0
                for ckey,cvalue in config.items():
                    if ckey not in ['jishul','jishuh']:
                        insurance_prob += float(cvalue.strip())
                print(insurance_prob)
                jishul = float(config['jishul'].strip())
                jishuh = float(config['jishuh'].strip())
                if value>=0 and value< jishul:
                    insurance = jishul*insurance_prob
                elif value >= jishul and value <= jishuh:
                    insurance = value* insurance_prob
                elif value> jishuh:
                    insurance = jishuh*insurance_prob
                sd_tax = value - insurance - start_point
                if sd_tax <=0 :
                    t = 0
                    num =0
                elif sd_tax>0 and  sd_tax<=1500:
                    t = 0.03
                    num = 0
                elif sd_tax>1500 and sd_tax<=4500:
                    t = 0.1
                    num = 105
                elif sd_tax>4500 and sd_tax<=9000:
                    t = 0.2
                    num = 555
                elif sd_tax>9000 and sd_tax<=35000:
                    t = 0.25
                    num = 1005
                elif sd_tax>35000 and sd_tax<=55000:
                    t = 0.30
                    num = 2755
                elif sd_tax>55000 and sd_tax<=80000:
                    t = 0.35
                    num = 5505
                elif sd_tax>80000:
                    t = 0.45
                    num = 13505

                final_tax =abs(sd_tax*t - num)
                salary_taxed = format(value-final_tax-insurance,".2f")
                insurance_2f = format(insurance,".2f")
                final_tax_2f = format(final_tax,'.2f')
                t =datetime.datetime.now()
                t_str = datetime.datetime.strftime(t,'%Y-%m-%d %H:%M:%S')
              
                user_output = [key,value,insurance_2f,final_tax_2f,salary_taxed,t_str]
                all_user_output.append(user_output)
            queue2.put(all_user_output) 
        except:
            print("Parameter Error") 
        
    def export(self,export_file,default = 'csv'):
        result = queue2.get(timeout= 1)
        print(result)
        with open(export_file,'a') as f :
            writer = csv.writer(f)
            writer.writerows(result)
        
                
    def main(self):
        Arg = Args()
        file_road = Arg.read_fileroad()
        userfile = file_road['userdata']
        #print(userfile)
        export_file = file_road['resultdata']
        #print(export_file)
        p1 = Process(target =self.read_users_data(userfile),args =(userfile,))
        p2 = Process(target = self.calc_for_all_userdata())
        p3 = Process(target = self.export(export_file),args = (export_file,))
        p1.start()
        p2.start()
        p3.start()
        p1.join()
        p2.join()       
        p3.join()

if __name__ =='__main__':
    
    Income = IncomeTaxCalculator()
    Income.main()
    
   # print(Config._read_config(cfg_file))
    
