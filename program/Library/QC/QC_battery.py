import smbus
from argparse import ArgumentParser

ADDR_I2C = 0x0b
ADDR_RELATIVESTATEOFCHARGE = 0x0D
ADDR_ABSOLUTESTATEOFCHARGE = 0x0E
ADDR_REMAININGCAPACITY = 0x0F
ADDR_BATTERY_STATUS = 0x16

i2c_ch = 1
bus = smbus.SMBus(i2c_ch)

def check_all():
    
    try :        
        rel_charge = bus.read_i2c_block_data(ADDR_I2C, ADDR_RELATIVESTATEOFCHARGE, 1)[0]
        abs_charge = bus.read_i2c_block_data(ADDR_I2C, ADDR_ABSOLUTESTATEOFCHARGE, 1)[0]
        remaining = bus.read_i2c_block_data(ADDR_I2C, ADDR_REMAININGCAPACITY, 1)[0]
        status = bus.read_i2c_block_data(ADDR_I2C, ADDR_BATTERY_STATUS, 1)[0]
                
        if isinstance(rel_charge,int) and isinstance(abs_charge,int) and\
        isinstance(remaining,int) and isinstance(status,int):
            print('PASS')
        
    except Exception as e:
        print("FAIL")

def check_rel():
    try :
        rel_charge = bus.read_i2c_block_data(ADDR_I2C, ADDR_RELATIVESTATEOFCHARGE, 1)[0]
        print('PASS'if isinstance(rel_charge,int) else 'FAIL')   
    except Exception as e:
            print("FAIL")

def check_abs():
    try :
        abs_charge = bus.read_i2c_block_data(ADDR_I2C, ADDR_ABSOLUTESTATEOFCHARGE, 1)[0]
        print('PASS'if isinstance(abs_charge,int) else 'FAIL')   
    except Exception as e:
            print("FAIL")
            
def check_remaining():
    try :
        remaining = bus.read_i2c_block_data(ADDR_I2C, ADDR_REMAININGCAPACITY, 1)[0]
        print('PASS'if isinstance(remaining,int) else 'FAIL')   
    except Exception as e:
            print("FAIL")
            
def check_status():
    try :
        status = bus.read_i2c_block_data(ADDR_I2C, ADDR_BATTERY_STATUS, 1)[0]
        print('PASS'if isinstance(status,int) else 'FAIL')   
    except Exception as e:
            print("FAIL")            
            

if __name__ == '__main__':

    parser = ArgumentParser()
    
    parser.add_argument("--rel_charge", type=bool, default=False, help="rel_charge")
    parser.add_argument("--abs_charge", type=bool, default=False, help="abs_charge")
    parser.add_argument("--remaining", type=bool, default=False, help="remaining")
    parser.add_argument("--status", type=bool, default=False, help="status")
    
    
    args = parser.parse_args()

    
    if args.rel_charge : check_rel()
    if args.abs_charge : check_abs()
    if args.remaining : check_remaining()
    if args.status : check_status()
    
    if not(args.rel_charge \
           or args.abs_charge \
           or args.remaining \
           or args.status):
        check_all()
    