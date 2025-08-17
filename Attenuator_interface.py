###################################################################################################
#
#  Python library file to use with Mini-Circuits programmable Attenuator (Product ID 0x23)
#  This library use Libusb , PyUSB libraries
#  To use under Linux, Windows, OS
#  For Windows:
#  1. pip install libusb
#  2. pip install pyusb
#  3. copy libusb-1.0.dll (amd64 or x86 version according to Python ver 32/64 to Sys folder System32 or SysWow64) or add the path of the dll.
#  For Linux:
#  1. pip install libusb
#  2. pip install pyusb
#
##################################################################################################
import platform
import usb.core
import usb.util


class USBDAT:
    cmd1 = [0] * 64  # 64-byte command array

    def __init__(self):
        # Find the device
        self.dev = usb.core.find(idVendor=0x20ce, idProduct=0x0023)
        if self.dev is None:
            raise ValueError("Device not found")

        # Handle Linux-specific driver detachment
        if platform.system() == "Linux":
            for configuration in self.dev:
                for interface in configuration:
                    ifnum = interface.bInterfaceNumber
                    if not self.dev.is_kernel_driver_active(ifnum):
                        continue
                    try:
                        self.dev.detach_kernel_driver(ifnum)
                    except usb.core.USBError:
                        pass

        # Set USB configuration
        self.dev.set_configuration()

        # Get serial number
        self.cmd1[0] = 41
        self.dev.write(0x01, self.cmd1)
        s = self.dev.read(0x81, 64)
        self.SerialNumber = "".join(chr(s[i]) for i in range(1, len(s)) if s[i] > 0)

        # Get model name
        self.cmd1[0] = 40
        self.dev.write(0x01, self.cmd1)
        s = self.dev.read(0x81, 64)
        self.ModelName = "".join(chr(s[i]) for i in range(1, len(s)) if s[i] > 0)

    def ReadSN(self):
        return self.SerialNumber

    def ReadMN(self):
        return self.ModelName

    def Send_SCPI(self, SCPIcmd):
        self.cmd1[0] = 42
        for indx, char in enumerate(SCPIcmd, start=1):
            self.cmd1[indx] = ord(char)
        self.cmd1[len(SCPIcmd) + 1] = 0
        self.dev.write(0x01, self.cmd1)

        s = self.dev.read(0x81, 64)
        return "".join(chr(s[i]) for i in range(1, len(s)) if s[i] > 0)


# Initialize the device
try:
    U1 = USBDAT()
    print("Device connected successfully!")
    print("Device Model:", U1.ReadMN())
    print("Serial Number:", U1.ReadSN())
except Exception as e:
    print(f"Failed to initialize the device: {e}")
    exit()


# Functions for setting/querying attenuation
def set_attenuation(channel, value):
    """Set the attenuation value for a specific channel."""
    if 1 <= channel <= 4:
        SCPIcmd = f":CHAN:{channel}:SETATT:{value}"
        response = U1.Send_SCPI(SCPIcmd)
        print(f"Channel {channel} attenuation set to {value} dB. Response: {response}")
    else:
        print("Invalid channel. Please select a channel between 1 and 4.")


def set_attenuation_sequential():
    """Set attenuation for all channels sequentially."""
    for channel in range(1, 5):
        try:
            value = float(input(f"Enter attenuation value for Channel {channel} (in dB): "))
            set_attenuation(channel, value)
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    print("All channels have been configured sequentially.")


def query_attenuation(channel=None):
    """Query the attenuation value for a specific channel or all channels."""
    if channel:
        if 1 <= channel <= 4:
            SCPIcmd = f":CHAN:{channel}:ATT?"
            response = U1.Send_SCPI(SCPIcmd)
            print(f"Channel {channel} attenuation: {response} dB.")
        else:
            print("Invalid channel. Please select a channel between 1 and 4.")
    else:
        SCPIcmd = ":ATT?"
        response = U1.Send_SCPI(SCPIcmd)
        print(f"All channel attenuations: {response}")


# Interactive menu
def menu():
    """Display the menu and handle user input."""
    while True:
        print("\n--- Mini-Circuits Attenuator Control ---")
        print("1. Set attenuation for a specific channel")
        print("2. Set attenuation for all channels sequentially")
        print("3. Query attenuation for a specific channel")
        print("4. Query attenuation for all channels")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            try:
                channel = int(input("Enter channel number (1-4): "))
                value = float(input("Enter attenuation value (in dB): "))
                set_attenuation(channel, value)
            except ValueError:
                print("Invalid input. Please enter valid numbers.")
        elif choice == "2":
            set_attenuation_sequential()
        elif choice == "3":
            try:
                channel = int(input("Enter channel number (1-4): "))
                query_attenuation(channel)
            except ValueError:
                print("Invalid input. Please enter a valid number.")
        elif choice == "4":
            query_attenuation()
        elif choice == "5":
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please try again.")


# Run the menu for user interaction
try:
    menu()
except KeyboardInterrupt:
    print("\nProgram interrupted by user. Exiting.")