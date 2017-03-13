# coding=utf-8
# FileName: GitHubForWindowsSpider.py
# Function: 解决GitHub for Windows无法安装问题，自动下载所需要的安装文件，全部下载完成后直接运行GitHub.application即可
# Author: kai.wang (clomis)
# Time: 2017/03/13
# Version: 0.1

import xml.dom.minidom
import urllib.request
import os

# ########################################
# 下载GitHub.application文件
# 解析出GitHub.exe.manifest文件下载地址
# 解析出GitHub版本
# ########################################
GitHub_application_Url = "http://github-windows.s3.amazonaws.com/GitHub.application"
GitHub_application_Local = './GitHub.application'
print("DownLoading File: GitHub.application from " + GitHub_application_Url)
urllib.request.urlretrieve(GitHub_application_Url, GitHub_application_Local)

# 打开XML文档
GitHub_application_DOM = xml.dom.minidom.parse(GitHub_application_Local)
# 得到文档元素对象
GitHub_application_Element = GitHub_application_DOM.documentElement


# 获取assemblyIdentity节点，GitHub版本和应用文件的存储路径
GitHub_exe_version = ""
GitHub_ApplicationFiles_Local = './Application Files/GitHub_'
GitHub_exe_manifest_Version_Node = GitHub_application_Element.getElementsByTagName('assemblyIdentity')[1]
if GitHub_exe_manifest_Version_Node.hasAttribute('version'):
    GitHub_exe_version = GitHub_exe_manifest_Version_Node.getAttribute('version')
    GitHub_ApplicationFiles_Local += GitHub_exe_version.replace('.', '_') + '/'   # 版本号中的.替换为路径中使用的字符_

if os.path.exists(GitHub_ApplicationFiles_Local) == False:
    print("Application Dir is not Found, Then Create it!")
    os.makedirs(GitHub_ApplicationFiles_Local)


# 获取dependentAssembly节点，构造GitHub.exe.manifest地址，形如Application Files/GitHub_3_3_4_0/GitHub.exe.manifest
GitHub_exe_manifest_Url = "http://github-windows.s3.amazonaws.com/"
GitHub_exe_manifest_CodeBase_Node = GitHub_application_Element.getElementsByTagName('dependentAssembly')[0]
if GitHub_exe_manifest_CodeBase_Node.hasAttribute("codebase"):
    GitHub_exe_manifest_Url += (GitHub_exe_manifest_CodeBase_Node.getAttribute("codebase")).replace('\\', '/')  # \替换为URL中的/

GitHub_exe_manifest_Local = GitHub_ApplicationFiles_Local + "GitHub.exe.manifest"

# ########################################
# 下载GitHub.exe.manifest文件
# ########################################
GitHub_exe_manifest_Url = urllib.request.quote(GitHub_exe_manifest_Url, ":/")
print("DownLoading File: GitHub.exe.manifest from " + GitHub_exe_manifest_Url)
urllib.request.urlretrieve(GitHub_exe_manifest_Url, GitHub_exe_manifest_Local)



# ########################################
# 解析manifest文件依次下载
# ########################################
GitHub_exe_manifest_DOM = xml.dom.minidom.parse(GitHub_exe_manifest_Local)
GitHUb_exe_manifest_Element = GitHub_exe_manifest_DOM.documentElement

# 获取所有的dependentAssembly节点，查找codebase属性
dependentAssembly_Nodes = GitHUb_exe_manifest_Element.getElementsByTagName('dependentAssembly')
print("Scanning for codebase Attr. in dependentAssembly Nodes:")
for node in dependentAssembly_Nodes:
    if node.hasAttribute("codebase"):
        print("  |-- " + node.getAttribute("codebase") + " Searched. DownLoad it!")
        codebase = node.getAttribute("codebase").split("\\")    # \号分隔，判断是否包含目录
        size = int(node.getAttribute("size"))
        srcfile_Url = 'http://github-windows.s3.amazonaws.com/Application Files/GitHub_' + GitHub_exe_version.replace('.', '_') + '/'
        dstfile_Local = GitHub_ApplicationFiles_Local
        if os.path.exists(dstfile_Local + node.getAttribute("codebase")):   # 文件存在
            if os.path.getsize(dstfile_Local + node.getAttribute("codebase")) != size:  # 判断文件大小是否正确
                print("       File is Existed, but non-Completed. ReLoading: " + dstfile_Local + node.getAttribute("codebase"))
            else:
                print("       File is Existed, Ignored: " + dstfile_Local + node.getAttribute(
                    "codebase"))
                continue

        if len(codebase) == 1:
            srcfile_Url += codebase[0] + '.deploy'
            dstfile_Local += codebase[0] + '.deploy'
        else:
            if os.path.exists(GitHub_ApplicationFiles_Local + codebase[0]) == False:
                os.makedirs(GitHub_ApplicationFiles_Local + codebase[0])
            srcfile_Url += codebase[0] + "/" + codebase[1] + '.deploy'
            dstfile_Local += codebase[0] + "\\" + codebase[1] + '.deploy'

        srcfile_Url = urllib.request.quote(srcfile_Url, ":/")
        print("       From: " + srcfile_Url + '\t To: ' + dstfile_Local)
        urllib.request.urlretrieve(srcfile_Url, dstfile_Local)
        print("       DownLoading Over!")

# 获取所有的file节点，查找name属性
file_Nodes = GitHUb_exe_manifest_Element.getElementsByTagName('file')
print("Scanning for name Attr. in file Nodes:")
for node in file_Nodes:
    if node.hasAttribute("name"):
        print("  |-- " + node.getAttribute("name") + " Searched. DownLoad it!")
        name = node.getAttribute("name").split("\\")    # \号分隔，判断是否包含目录
        size = int(node.getAttribute("size"))
        srcfile_Url = 'http://github-windows.s3.amazonaws.com/Application Files/GitHub_' + GitHub_exe_version.replace('.', '_') + '/'
        dstfile_Local = GitHub_ApplicationFiles_Local
        if os.path.exists(dstfile_Local + node.getAttribute("name")):
            if os.path.getsize(dstfile_Local + node.getAttribute("name")) != size:
                print("       File is Existed, but not Completed. Reloading: " + dstfile_Local + node.getAttribute("name"))
            else:
                print("       File is Existed, Ignored: " + dstfile_Local + node.getAttribute("name"))
                continue

        if len(name) == 1:
            srcfile_Url += name[0] + '.deploy'
            dstfile_Local += name[0] + '.deploy'
        else:
            if os.path.exists(GitHub_ApplicationFiles_Local + name[0]) == False:
                os.makedirs(GitHub_ApplicationFiles_Local + name[0])
            srcfile_Url += name[0] + "/" + name[1] + '.deploy'
            dstfile_Local += name[0] + "\\" + name[1] + '.deploy'
        srcfile_Url = urllib.request.quote(srcfile_Url, ":/")
        print("       From: " + srcfile_Url + '\t To: ' + dstfile_Local)
        urllib.request.urlretrieve(srcfile_Url, dstfile_Local)
        print("       DownLoading Over!")
