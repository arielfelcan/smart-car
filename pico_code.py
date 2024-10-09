from machine import Pin, PWM, I2C
from mqtt import MQTTClient
import time, mqtt

if True:
    import network
    import time

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect('Tufts_Robot', '')

    print('Wi-Fi connection pending', end = '')
    while wlan.ifconfig()[0] == '0.0.0.0':
        print('.', end='')
        time.sleep(1)

    # We should have a valid IP now via DHCP
    print('\nWi-Fi connection successful: {}'.format(wlan.ifconfig()))
  

class PID:
    def __init__(self):
        self.left1 = PWM(Pin('GPIO12', Pin.OUT)) # will be in different class eventually
        self.left1.freq(100)
        self.left2 = PWM(Pin('GPIO13', Pin.OUT))
        self.left2.freq(100)
        self.left2.duty_u16(0)
        self.left1.duty_u16(0)

        self.right1 = PWM(Pin('GPIO16', Pin.OUT))
        self.right1.freq(100)
        self.right2 = PWM(Pin('GPIO17', Pin.OUT))
        self.right2.freq(100)
        self.right2.duty_u16(0)
        self.right1.duty_u16(0)
        
        self.buzzer_pwm = PWM(Pin(18, Pin.OUT))  # GPIO18 pin
        
        self.curr_duty = 30000
        
        self.mqtt_sub()
    
    def forward_R(self, duty):
        self.right1.duty_u16(duty)
        self.right2.duty_u16(0)

    def backward_R(self, duty):
        self.right1.duty_u16(0)
        self.right2.duty_u16(duty)
    
    def stop_R(self):
        self.right1.duty_u16(0)
        self.right2.duty_u16(0)
        
    def forward_L(self, duty):
        self.left1.duty_u16(duty)
        self.left2.duty_u16(0)

    def backward_L(self, duty):
        self.left1.duty_u16(0)
        self.left2.duty_u16(duty)
    
    def stop_L(self):
        self.left1.duty_u16(0)
        self.left2.duty_u16(0)
    
    def mqtt_sub(self):
        self.stop_R()
        mqtt_broker = 'broker.hivemq.com' 
        port = 1883
        topic = 'ME35-24/Rachael'       # this reads anything sent to ME35
        
        def callback(topic, msg):
            topic, msg = topic.decode(), msg.decode()
            print(topic, msg)
            
            adjust = round(float(msg))
            
            self.curr_duty = self.curr_duty + adjust
            print(self.curr_duty)
            
            self.forward_R(self.curr_duty)
            self.forward_L(self.curr_duty)

        
        client = MQTTClient('PriusR', mqtt_broker, port, keepalive=60)
        client.set_callback(callback)
        client.connect()
        client.subscribe(topic.encode())

        while True:
            client.check_msg()
            time.sleep(0.01)

go = PID()
