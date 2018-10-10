import time
import io
import binascii
import codecs
import serial
ser = serial.Serial('/dev/ttyUSB0', 96000, timeout=1.0)
if ser.isOpen():
    print(ser.name + ' is open...')
    ser.flush()
while True:
    cmd = input("Enter command or 'exit':")
    byt = ser.inWaiting()
    n=0
    if byt > 0:
        print(ser.read(byt))
    elif cmd == 'exit':
        ser.close()
        exit()
    elif cmd == 'flush':
        ser.flush()
        print("flushed, bytes in waiting: "+ str(byt))
    elif cmd == 'bytes':
        print('bytes in waiting: '+str(byt))
    else:
        if ser.inWaiting()==0:
            while ser.inWaiting()==0 and n < 6:
                ser.write(codecs.encode(cmd))
                print('waiting...')
                time.sleep(.1)
                print(ser.readline(30))
                print('resending command: '+str(codecs.encode(cmd))+' retry #'+str(n))
                ser.write(codecs.encode(cmd))
                n = n + 1
                print(ser.readline(30))
                time.sleep(.1)
                if n == 6:
                    print('No Response Received')
        byt = ser.inWaiting()
        while byt > 0 and  ser.readline(byt)!=bytes():
            msg = ser.readline(byt+20)
            msg_str = str(msg)
            #msg_hex = msg.decode('ascii')
            print(msg_str)
            
            #print(msgascii)
    #else:
     #   ser.write(str.encode(cmd))
      #  byt = ser.inWaiting()
       # out = ser.readline(byt)
       # while True:
        #    if out == b'':
         #       print('No Response')
         #   else:
          #      print(out)
