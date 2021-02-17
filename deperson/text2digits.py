import urllib3
import pandas as pd
import requests
import pickle
from bs4 import BeautifulSoup



class dutch_numtext_to_text:
    
    """ This class involves two main methods. 
    1. wordsbunbers_to_digits1 => returns the dutch text given any digit taken as input
    2. text2int => returns the digit from the range 0-100 taking as an input the corresponding dutch text"""
    
    num2word = 'https://clevert.com.br/t/en/numbers_to_words/generate'
    word2num = 'http://www.marijn.org/everything-is-4/counting-0-to-100/dutch/'
    
    def __init__(self, lang, n2w_link = num2word, w2n_link = word2num):
        
        self.n2w_link = n2w_link
        self.w2n_link = w2n_link
        self.lang = lang
        
        
    def wordsbunbers_to_digits1(self, number):
    
        """The method that returns the dutch text taking as an input any number"""
    
        http = urllib3.PoolManager()
        number = str(number)
        response = http.request('GET', self.n2w_link + '?number='+number+'&numLanguage='+self.lang)
        status = 'The response status is ' + str(response.status)
        data = response.data
        data = data.decode('utf-8')
        data = data.replace('\xad', '')
    
        return data,status
    
    @staticmethod
    def get_dutch_nums_dict(url):
    
        """The method that creates the dictionary mapping every text number from 0-100 to the corresponging digit"""
    
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        output_rows = []
        for table_row in table.findAll('tr'):
            columns = table_row.findAll('td')
            output_row = []
            for column in columns:
                output_row.append(column.text)
            output_rows.append(output_row)
        list2 = [x for x in output_rows if x]
        nums = {}
        for elem in list2:

            num = int(elem[0])
            if elem[1]:
                elem[1] = elem[1].replace('Ã«','ë')
            nums[elem[1]] = num

        return nums
    
    def t2int(self,text):
    
        """The method that creates the pickle file containig the dictionary with text number to digit mapping"""
    
        target = self.w2n_link
        d_nums = self.get_dutch_nums_dict(target)
        
        with open('d_nums.pkl', 'wb') as output_file:
            pickle.dump(d_nums, output_file)
            
        with open('d_nums.pkl', 'rb') as input_file:
            dict_nums = pickle.load(input_file)
            
        n_list = list(dict_nums.keys())

        num = -1
        if text in n_list:
            num = dict_nums[text]   

        return num
    
    def text2int(self,text):
    
        """The method that returns the digit given a text number as an input between 0-100"""

        with open('d_nums.pkl', 'rb') as input_file:
            dict_nums = pickle.load(input_file)
            
        n_list = list(dict_nums.keys())

        num = -1
        if text in n_list:
            num = dict_nums[text]   

        return num

if __name__ == '__main__':
    
    lang = 'nl'
    textnum = input ("Enter the dutch text of a number between 0-100:") #'negenennegentig'
    numtext = input ("Enter any number between:")
    
    obj = dutch_numtext_to_text(lang)
    print(obj.text2int(textnum))
    print(obj.wordsbunbers_to_digits1(numtext))