from distutils.core import setup, Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext
from os import listdir, removedirs,path,remove, rename
from os.path import isfile, isdir, join
from shutil import copytree, rmtree
import sysconfig

def get_ext_filename_without_platform_suffix(filename):
	name,ext = path.splitext(filename)
	ext_suffix = sysconfig.get_config_var('EXT_SUFFIX')
	
	if ext_suffix == ext:
		return filename
		
	ext_suffix = ext_suffix.replace(ext,'')
	idx=name.find(ext_suffix)
	
	if idx == -1:
		return filename
	else:
		return name[:idx] + ext
	
class BuildExtWithoutPlatformSuffix(build_ext):
	def get_ext_filename(self, ext_name):
		filename = super().get_ext_filename(ext_name)
		return get_ext_filename_without_platform_suffix(filename)

def programPy2So(path,ignore_dir,ignore_file):
	try:
		temp_name = ''
		for f in listdir(path):
			if f == '__init__.py':
				print("__init__.py bug protect.")
				rename(join(path,f),join(path,'temp_init'))
				temp_name = f
		for f in listdir(path):
			full_path = join(path,f)
			if isfile(full_path):
				if not f in ignore_file:
					if(f[-2:] == 'py'):
						setup(
							ext_modules = cythonize(full_path,language_level = "3"),
							cmdclass = {'build_ext' : BuildExtWithoutPlatformSuffix},
							options={'build':{'build_lib':path}}
						)
						remove(full_path[:-3]+".c")
						remove(full_path)
				else:
					print("Ignore file",f)
			elif isdir(full_path):
				if f in ignore_dir:
					print("Ignore dir",f)
				else:
					programPy2So(full_path,ignore_dir,ignore_file)
		if(temp_name != ''):
			rename(join(path,'temp_init'),join(path,temp_name))
	except Exception as e:
		print(e)

#-------------------------Package dir 1------------------------------
program_dir = './program'
ignore_dir = ['SW_flow_test','algorithm','SW_test']
#Ignore the execute file.
ignore_file = ['main.py']
print("Start package the ",program_dir," dir.")
programPy2So(program_dir+'_ext',ignore_dir,ignore_file)

#-------------------------Package dir 2------------------------------
program_dir = './server'
ignore_dir = ['']
#Ignore the execute file.
ignore_file = ['server.py','statusServer.py']
print("Start package the ",program_dir," dir.")
programPy2So(program_dir+'_ext',ignore_dir,ignore_file)

#-------------------------Package dir 3------------------------------
program_dir = './tool_sh'
ignore_dir = ['']
#Ignore the execute file.
ignore_file = ['wifi_search.py','start_NTP.py','reset.py']
print("Start package the ",program_dir," dir.")
programPy2So(program_dir+'_ext',ignore_dir,ignore_file)


#-------------------------Package dir 4------------------------------
program_dir = './OTA'
ignore_dir = ['']
#Ignore the execute file.
ignore_file = ['setup.py']
print("Start package the ",program_dir," dir.")
programPy2So(program_dir+'_ext',ignore_dir,ignore_file)
