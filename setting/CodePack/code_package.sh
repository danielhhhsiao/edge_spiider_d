#!/bin/sh

#Input your relatively path
executable_ori_path=("./program" "./server" "./tool_sh" "./OTA")

for((i=0; i<${#executable_ori_path[@]}; i++))
do
	executable_path[i]="${executable_ori_path[i]}_ext"
	if [ -d "${executable_path[i]}" ]; then
		rm -r "${executable_path[i]}"
		echo "Remove pre_dir."
	fi
	sudo cp -r "${executable_ori_path[i]}/" "${executable_path[i]}"
	sudo chmod -R 777 "${executable_path[i]}"
done

#Input your execute file after "${executable_path[N]}/
#N depend on the executable_ori_path index.
#(Don't include the Filename Extension.)
executable_list=("${executable_path[0]}/main" "${executable_path[1]}/statusServer" "${executable_path[1]}/server" "${executable_path[2]}/wifi_search" "${executable_path[2]}/start_NTP" "${executable_path[3]}/setup")

#Package the executable_list
for((i=0; i<${#executable_list[@]}; i++))
do
	echo "Package the file:${executable_list[i]}.py"
	sudo cython --embed -o "${executable_list[i]}.c" "${executable_list[i]}.py" -3
	sudo gcc -Os -I /usr/include/python3.7m -o "${executable_list[i]}" "${executable_list[i]}.c" -lpython3.7m -lpthread -lm -lutil -ldl
	echo "Success for package. Remove the origin file."
	sudo rm "${executable_list[i]}.py"
	sudo rm "${executable_list[i]}.c"
done

#py file to .so
sudo python3 set.py build
if [ -d "./build" ]; then
	sudo rm -r ./build
	echo "Remove build dir."
fi
for((i=0; i<${#executable_ori_path[@]}; i++))
do
	sudo chmod -R 777 "${executable_path[i]}"
done
echo "Code-Package completed."
