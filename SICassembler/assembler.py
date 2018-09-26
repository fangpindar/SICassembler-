# -*- coding: utf-8 -*-
"""
Created on Thu May  3 21:40:02 2018

@author: shiraishi mai
"""
opcode = {
    "ADD":"18", "AND":"40", "COMP":"28",    "DIV":"24", "J":"3C",   "JEQ":"30",
    "JGT":"34", "JLT":"38", "JSUB":"48",    "LDA":"00", "LDCH":"50",    "LDL":"08",
    "LDX":"04", "MUL":"20", "OR":"44",  "RD":"D8",  "RSUB":"4C",    "STA":"0C",
    "STCH":"54",    "STL":"14", "STSW":"E8",    "STX":"10", "SUB":"1C", "TD":"E0",
    "TIX":"2C", "WD":"DC"}

R1=" **** odd length hex string in byte statement"
R2=" **** illegal operand in word statement"

file = open('./SRCFILE', 'r')
out = open('out.txt', 'w')

#print (file.readline())
arr = []
while True:
    line = file.readline().strip().split()
    if not line:
        break
    if len(line) < 3:
        line.insert(0, '')
    arr.append(line)

#print (arr)

'''
pass 1 start
'''
LOCCTR = 0

for i in arr:
    if len(i) > 1 and i[1] == 'START':
      if LOCCTR == 0:
          LOCCTR = int('0x' + arr[0][arr[0].index('START') + 1], 0)
      else:
          print ('Error: Duplicate START statement.')
#print (LOCCTR)

SYMTAB = {'rsub': 0}

for line in arr:
    if line[1].upper() == 'RSUB':
        out.writelines('{}\t{}\t\t{}\t\n'.format(hex(LOCCTR), line[0], line[1]))
    else:
        out.writelines('{}\t{}\t\t{}\t{}\n'.format(hex(LOCCTR), line[0], line[1], line[2]))
    if line[0] != '':
        if line[0] in SYMTAB:
            print ('Error: Duplicate symbol.')
        else:
            SYMTAB[line[0]] = LOCCTR
            
    if line[1].upper() =='START' or line[1].upper() =='END': 
        continue
    if line[1].upper() == 'RESB':
        LOCCTR += int(line[2])
    elif line[1].upper() == 'RESW':
        LOCCTR += int(line[2]) * 3
    elif line[1].upper() == 'BYTE':
        if line[2][0].upper() == 'X':
            LOCCTR += int((len(line[2])-3)/2)
        elif line[2][0].upper() == 'C':
            LOCCTR += int(len(line[2])-3)
    else:
        LOCCTR += 3
 
#for elem in SYMTAB:
#    print (elem, ':', hex(SYMTAB[elem]))

file.close()
out.close()

#print ('Pass 1 done.')
    
''' 
pass 2 start
'''

out = open('out.txt', 'r')

arr = []
while True:
    line = out.readline().strip().split()
    if not line:
        break
    if len(line) <= 3:
        line.insert(1, '')
        
    arr.append(line)
#print (arr)
Ctemp=[]
for index, line in enumerate(arr):
    obcode=""
    
    if line[2].upper() == 'RSUB':
        arr[index].append(' ')
        obcode = '4C0000'
    elif line[2].upper() == 'START' or line[2].upper() == 'END':
        arr[index].append(obcode)#place "" inside
        continue
    elif line[2].upper() == 'RESW' or line[2].upper() == 'RESB':
        arr[index].append(obcode)#place "" inside
        continue
    elif line[2].upper() == 'BYTE':
        if line[3][0].upper() == 'X':
            if len(line[3][2:-1]) % 2 != 0:
                obcode="R1"#'Error: Odd length hex string in byte statement.'
                arr[index].append(obcode)#place error inside
                continue
            else:
                obcode = line[3][2:-1]
        elif line[3][0].upper() == 'C':
            for char in line[3][2:-1]:
                obcode += str(hex(ord(char))[2:])
    elif line[2].upper() == 'WORD':
        if not line[3].isdigit():
            obcode="R2"#'Error: Illegal operand in word statement.'
            arr[index].append(obcode)#place error inside
            continue
        else:
            obcode = hex(int(line[3]))[2:].zfill(6)
    else:
        if ',x'in line[3]:
        # add x register reference
            Ctemp=line[3].split(',')
            obcode += opcode[line[2].upper()] + str(hex(SYMTAB[Ctemp[0]]+32768)[2:])
        else:
            obcode += opcode[line[2].upper()] + str(hex(SYMTAB[line[3]])[2:])            
    arr[index].append(obcode)#place the correct obcode

#print (obcode)

    
#######################################################
    #LISFILE
file = open('./LISFILE', 'w')

for i in range(len(arr)):
    arr[i][0]=arr[i][0][2:]#hex without 0x
    arr[i][0]=arr[i][0].zfill(4)#fill until 4 bit
    
    temp=""
    if arr[i][4]=="":
        temp=arr[i][0]+" "+"      "+" "+arr[i][1].ljust(8)+" "+arr[i][2].ljust(7)+" "+arr[i][3]
    elif arr[i][4][0]=="R":#check if it's a wrong obcode
        temp=arr[i][0]+" "+"      "+" "+arr[i][1].ljust(8)+" "+arr[i][2].ljust(7)+" "+arr[i][3]
        file.write(temp+"\n")
        if arr[i][4]=="R1":
            file.write(R1+"\n")
        elif arr[i][4]=="R2":
            file.write(R2+"\n")
        continue
    elif arr[i][2]=="BYTE" and arr[i][3][0]=="C":#need to change to char
        temp=arr[i][0]+" "
        Ctemp=""
        for j in range(int(len(arr[i][4])/2)):
            temp=arr[i][4][j*2]+arr[i][4][j*2+1]#every chose 2 bit
            Ctemp+=chr(int(temp,16))
        temp+=Ctemp.ljust(6)
        temp+=" "+arr[i][1].ljust(8)+" "+arr[i][2].ljust(7)+" "+arr[i][3]#reast of the string
    else:
        temp=arr[i][0]+" "+arr[i][4].ljust(6)+" "+arr[i][1].ljust(8)+" "+arr[i][2].ljust(7)+" "+arr[i][3]
    file.write(temp+"\n")
file.close()
#######################################################
    #OBJFILE H
file = open('./OBJFILE', 'w')

Hcard="H"
ProgramName=arr[0][1]
Hcard+=ProgramName

ProgramStart=arr[0][0].zfill(6)#fill like 000000
Hcard+=ProgramStart

ProgramStart=int(arr[0][0],16)#hex to dec
ProgramEnd=int(arr[len(arr)-1][0],16)
ProgramLen=ProgramEnd-ProgramStart#dec
ProgramLen=hex(ProgramLen)[2:].zfill(6)
Hcard+=ProgramLen
file.write(Hcard+"\n")#H finish
#######################################################
    #OBJFILE T
T=""            #T+TLOCATE+TLEN+TTEMP
check=0
TTEMP=""
Tlen=0
Ctemp=[]
for i in range(len(arr)):
    if T=="" and arr[i][4]!="":#第一次，新的卡片，判斷法，T卡片空且現在的arr[i]
        T+="T"+arr[i][0].zfill(6)
        TTEMP+=arr[i][4]
        Tlen+=int(len(arr[i][4])/2)
    elif arr[i][2]!="START" :
        if Tlen+int(len(arr[i][4])/2)>30 or arr[i][4]=="":#如果長度加現在大於60了，或沒讀到obcode，儲存結束#
            T+=str(hex(Tlen)[2:]).zfill(2)+TTEMP+"\n"
            if T!="00\n":#防止印出END
                file.write(T)
            if arr[i][2]=="END":
                break
            T=""#Reset
            TTEMP=""
            Tlen=0

            if arr[i][4]!="":#如果當前有obcode
                T+="T"+arr[i][0].zfill(6)
                TTEMP+=arr[i][4]
                Tlen+=int(len(arr[i][4])/2)
            continue
        if arr[i][4][1]=="R":#有錯誤，直接結束，並且標示不需要E卡片了
            check==1
            break
        #以上兩個沒問題，開始放obcode到TTEMP
        if arr[i][3][0]=="C":
            Tlen+=int(len(arr[i][4])/2)
            if arr[i][3][1]=="'":
                Ctemp=arr[i][3].split("'")
                TTEMP+=Ctemp[1]
            else:
                TTEMP+=arr[i][4]#將正確可用的obcode存起來
        else:
            Tlen+=int(len(arr[i][4])/2)
            TTEMP+=arr[i][4]#將正確可用的obcode存起來

#######################################################
    #OBJFILE E
Ecard=""
if check!=1:
    Ecard="E"+arr[0][0].zfill(6)
    file.write(Ecard)
file.close()
    #E finish
#######################################################
for i in range(len(arr)):
    print(arr[i])
