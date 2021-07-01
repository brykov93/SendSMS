import os
import serial
import random
from time import sleep

def PhoneNumberToSMS(number):
    number += 'F'
    TP_DA = '0B' + '91'
    i = 0
    while i < len(number):
        TP_DA += number[i+1] + number[i]
        i += 2
    return TP_DA


def TextToSMS(text):
    global len_sms
    len_sms=''
    b = text
    result = ''
    i = 0
    while i < len(b):
        o = ord(b[i])
        result += ("%0.2X" % (o/256)) + ("%0.2X" % (o%256))
        i += 1
    return result


def get_len(text):
    num_cyr=0
    num_lat=0
    sym=0
    len_text=''
    for i in range(len(text)):
        if ord(text[i]) in range(1040,1103) or ord(text[i])==1105 or ord(text[i])==1025 :
            num_cyr=num_cyr+1
        elif ord(text[i]) in range(65,122):
            num_lat=num_lat+1
        else:
            sym=sym+1
    if num_cyr>num_lat:
        len_text=str(int(hex(len(text)*2)[2:],10))
    elif num_cyr<num_lat :
        len_text=str(len(text))
    if len(len_text)==1:
        len_text='0'+len_text
    return len_text

    
def send_sms(phone,text,modem="COM14"): 
    """Send SMS via GSM modem"""
    fd = serial.Serial('COM14', 115200,timeout = 1, xonxoff=True, dsrdtr = True, interCharTimeout = True)
    fd.write("AT+CMGF=0 \015")
    ans=fd.readline()
    print ans
    chunks = []
    if len(text) > 70:
        while len(text) > 66:
            chunks.append(text[:66])
            text = text[66:]
    if len(text) > 0:
        chunks.append(text)
    PDU_TYPE = "01"
    TP_MR = ""
    if len(chunks) > 1:
        PDU_TYPE = "41"
    elif len(chunks)==1:
        PDU_TYPE = "01"
        TP_MR='00'        
    i = 1
    TP_DA=PhoneNumberToSMS(phone)
    TP_PID='00'
    TP_DCS='08'
    TP_UDL= get_len(text)
    reference_number= ("%0.4X" % random.randint(1,65535))[2:].upper()
    i=1
    for chunk in chunks:
        TP_UD = TextToSMS(chunk)
        if TP_MR != "00":
            TP_MR = "%0.4X" % random.randint(1,65535)
            TP_MR = TP_MR[2:]
            TP_UD = "05" + "00" + "03" + reference_number + ("%0.2X" % len(chunks)) + ("%0.2X" % i) + TP_UD
            TP_UDL=str(hex(len(TP_UD)/2))[2:].upper()
            sms = '00' + PDU_TYPE + TP_MR + TP_DA + TP_PID + TP_DCS + TP_UDL + TP_UD
            fd.write('AT+CMGS=' + str(len(sms)/2-1) + '\015')
            sleep(0.5)
            ans=fd.readline()
            print ans
            fd.write(sms + '\032')
            sleep(0.5)
            ans=fd.readline()
            print ans
            sleep(0.5)
            print sms+'\n'
            i=i+1
        elif TP_MR == "00" :
            sms = '00' + PDU_TYPE + TP_MR + TP_DA + TP_PID + TP_DCS + TP_UDL + TP_UD
            fd.write('AT+CMGS=' + str(len(sms)/2-1) + '\015')
            sleep(0.5)
            ans=fd.readline()
            print ans
            fd.write(sms + '\032')
            sleep(0.5)
            ans=fd.readline()
            print ans
    fd.close()
    print "Send SMS to number %s. Text is: '%s'" % (phone, text)

if __name__ == "__main__":
    print "Send SMS"
    print "    Phone number:",
    phone = raw_input()
    print "    Text        :",
    text = raw_input().decode('cp1251')
    send_sms(phone, text, "COM14")
