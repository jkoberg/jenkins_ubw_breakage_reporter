
from contextlib import contextmanager
import serial, time

class UBWError(Exception): pass
class UBWProtocolError(UBWError): pass
class UBWCommandError(UBWError): pass


class USBBitWhacker(object):
  def __init__(self, port_name="COM7", port_options={}):
    self.port_name = port_name
    self.port_options = port_options

  def open(self):
    self._port = serial.Serial(self.port_name, timeout=0.25, **self.port_options)
    self.reset()
    self.get_version()
    
  def close(self):
    self._port.close()
    del self._port
    
  def command(self, cmdstring):
    self._port.flushInput()
    self._port.write(cmdstring.strip() + "\r\n")
    response = self._port.readline()
    if not response:
      raise UBWProtocolError("UBW did not respond to command")
    response = response.strip()
    if response[0] == '!':
      return UBWProtocolError(response)
    return response
    
  def reset(self):
    self.command("R")
    
  def get_version(self):
    self.version = self.command("V")
    return self.version
    
  def parse_pinspec(self, pinspec):
    if len(pinspec) < 2:
      raise UBWError("Pinspec must be 2 chars in the format 'A0'")
    pinspec = pinspec.upper()
    port = pinspec[0]
    pin = pinspec[1]
    if port not in 'ABC':
      raise UBWError("Pinspec must reference port A or B")
    if pin not in '01234567':
      raise UBWError("Pinspec must reference pin 0-7")
    return port, pin
    
    
  def set_pin_dir(self, pinspec, direction):
    port, pin = self.parse_pinspec(pinspec)
    if not direction or direction == "0" or direction == "out":
      direction = "0"
    else:
      direction = "1"
    return self.command("PD,%s,%s,%s" %(port, pin, direction))
    
  def set_to_output(self, pinspec):
    return self.set_pin_dir(pinspec, 'out')
    
  def set_to_input(self, pinspec):
    return self.set_pin_dir(pinspec, 'in')
  
  def set_output_state(self, pinspec, state):
    port, pin = self.parse_pinspec(pinspec)
    if not state or state == "0" or state == "off":
      state = "0"
    else:
      state = "1"
    return self.command("PO,%s,%s,%s" %(port, pin, state))
    
  def turn_on(self, pinspec):
    return self.set_output_state(pinspec, "on")
    
  def turn_off(self, pinspec):
    return self.set_output_state(pinspec, "off")
    
    
  def read_pin(self, pinspec):
    port, pin = self.parse_pinspec(pinspec)
    response = self.command("PI,%s,%s" %(port, pin))
    if response[0:3] == "PI,":
      return True if response[3] == '1' else False
      
      
      


@contextmanager
def UBW(port):
  ubw = USBBitWhacker(port)
  ubw.open()
  yield ubw
  ubw.close()
  
  


def main():
  with UBW('COM8') as ubw:
    ubw.set_to_output('A0')
    while True:
      ubw.turn_on('A0')
      time.sleep(0.5)
      ubw.turn_off('A0')
      time.sleep(0.5)


if __name__ == "__main__":
    main()

