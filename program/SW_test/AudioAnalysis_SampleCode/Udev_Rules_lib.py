import subprocess
from pprint import  pprint

def build_rules():
    #set rule file name
    rules_file_name = "98-usb-id-rule.rules"
    #load snd list
    usb_snd=[]
    snd_string = subprocess.Popen('ls /dev/snd/', shell=True, stdout = subprocess.PIPE)
    out, err = snd_string.communicate()
    snd_list =out.decode('utf-8').splitlines()
    for snd in snd_list:
        if (snd.startswith("pcm")) and (snd.endswith("c")):
            usb_snd.append(snd)
    #print(usb_snd)

    # load snd kernel
    kernel_num =[]
    for i in range(len(usb_snd)):
        kernel_string=subprocess.Popen('udevadm info -a -p  $(udevadm info -q path -n /dev/snd/%s)|grep KERNELS'%usb_snd[i], shell=True, stdout = subprocess.PIPE)
        out, err = kernel_string.communicate()
        kernel_list =out.decode('utf-8').splitlines()
        kernel_num.append(kernel_list[1].strip())
        #for i in range(len(kernel_list)):
            #kernel_list[i] = kernel_list[i].strip()

    #build rules
    rules = []
    for rule_num in range(len(kernel_num)):
        if rule_num == 0:
            rules.append("ACTION!=\"add\", GOTO=\"my_usb_audio_end\"\n\n")
        rules.append("%s, ATTR{id}=\"usb%d\"\n"%(kernel_num[rule_num],rule_num+1))
        
        if rule_num == len(kernel_num)-1:
            rules.append("\nLABEL=\"my_usb_audio_end\"")
         
    fp = open(rules_file_name ,"w")
    fp.writelines(rules)
    fp.close()

    #trigger rules

    # try:
    #     subprocess.Popen('sudo rm /etc/udev/rules.d/%s'%rules_file_name, shell=True)
    # except:
    #     print("%s is not existed!")
    subprocess.Popen('sudo cp %s /etc/udev/rules.d/%s'%(rules_file_name, rules_file_name), shell=True)
    subprocess.Popen('sudo udevadm control --reload-rules ;sudo udevadm trigger', shell=True)

    print("Please replug the device to apply the new location setting!")
    print(input("Press Enter after repluging the usb microphone!"))

if __name__ == "__main__":
    build_rules()
