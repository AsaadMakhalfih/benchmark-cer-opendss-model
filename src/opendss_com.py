import sys
import win32com.client


def main():
    DSS = dss_object()


def dss_object():
    # instantiate an OpenDSS object named as DSS
    # win32com.client.Dispatch('ProgID') to instantiate the interface of a certain program
    DSS = win32com.client.Dispatch('OpenDSSEngine.DSS')
    if not DSS.Start(0):
        print('Unable to start the OpenDSS Engine!')
        sys.exit()
    else:
        print('OpenDSS object has been instantiated...')
    # Suspend all forms from popping up - faster for the execution
    DSS.AllowForms = False
    return DSS


if __name__ == '__main__':
    main()
