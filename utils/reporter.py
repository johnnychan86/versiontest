#-*- coding:utf-8 -*-
'''
Created on Oct 23, 2012

@author: johnny
'''
import os
from errors import error
import base_utils


root_dir = base_utils.ROOT_PATH
root_dir += "/html"

REPORT_BASE = "report_base.html"

def read_template():
    file_path = os.path.join(root_dir, REPORT_BASE)
    try:
        base_report = open(file_path, 'r')
        report_str = base_report.read()
        base_report.close()
        return report_str
    except IOError:
        raise error.CommonError(
        "Read report template failed: file cannot open or not exist")
        

def write_report(start_time, time_comsum, data, report_dir):
    report_str = read_template()
    table = ""
    i = 1
    for meta in data:
        if meta['result'] == 'FAILED':
            klass = 'failed_line'
        else:
            klass = ''
            
        table_line = ("""
        <tr class="%s">
            <td class="id">%s</td>
            <td class="name">%s</td>
            <td class="start_time">%s</td>
            <td class="end_time">%s</td>
            <td class="result">%s</td>
            <td class="traceback">%s</td>
        </tr>""" % 
        (klass, i, meta['name'], meta['start_time'],
         meta['end_time'], meta['result'],
         meta['traceback']))
        
        table = table + table_line
        i = i + 1
    
    total = str(len(data))
    passed = str(count_passed(data))
    failed = str(count_failed(data))
    report_str = report_str.replace("{{replace}}", table)
    report_str = report_str.replace("{{start_time}}", start_time)
    report_str = report_str.replace("{{time_comsum}}", str(time_comsum))
    report_str = report_str.replace("{{total}}", total)
    report_str = report_str.replace("{{passed}}", passed)
    report_str = report_str.replace("{{failed}}", failed)
    
    path = os.path.join(report_dir, 'report.html')
    report_file = open(path, 'w')
    report_file.write(report_str)


def count_failed(data):
    count = 0
    for meta in data:
        if meta['result'] == "FAILED":
            count += 1
    
    return count

def count_passed(data):
    count = 0
    for meta in data:
        if meta['result'] == "PASSED":
            count += 1
    
    return count


if __name__ == "__main__":
    print read_template()        