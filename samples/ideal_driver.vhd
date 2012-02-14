library IEEE;
use IEEE.math_real.all;
use IEEE.std_logic_1164.all;
library IEEE_proposed;
use IEEE_proposed.electrical_systems.all;
use IEEE_proposed.energy_systems.all;

entity driver_ideal is
  generic (r_open     : resistance  := 1000.0;
           r_closed   : resistance  := 5.0;
           trans_time : real        := 500.0e-12;
           cap        : capacitance := 5.1e-12;
           delay      : time        := 0 ns);
    port(
        dig_input : in std_logic;
        terminal v_pwr : electrical;
        terminal v_gnd : electrical;
        terminal v_driver : electrical
    );
end driver_ideal;


architecture linear of driver_ideal is
  signal   d_input_inv : std_logic;
  signal   r_pu_sig : resistance := r_open;
  signal   r_pd_sig : resistance := r_open;
  quantity v_pu  across i_pu through v_pwr to v_driver;
  quantity r_pu     : resistance;
  quantity v_pd  across i_pd through v_driver to v_gnd;
  quantity r_pd     : resistance;
  quantity v_cap across i_cap through v_driver to v_gnd;
  quantity v_gc  across i_gc through v_gnd to v_driver;
  quantity v_pc  across i_pc through v_driver to v_pwr;
  constant isat  : current := 1.0e-14;        -- Saturation current [Amps]
  constant TempC : real    := 27.0;           -- Ambient Temperature [Degrees]
  constant TempK : real    := 273.0 + TempC;  -- Temperaure [Kelvin]
  constant vt    : real    := K*TempK/Q;      -- Thermal Voltage
begin
  d_input_inv <= not dig_input after delay;

  DetectPUState: process (dig_input)
  begin
    if (dig_input'event and dig_input = '0') then
      r_pu_sig <= r_open;
    elsif (dig_input'event and dig_input = '1') then
      r_pu_sig <= r_closed;
    end if;
  end process DetectPUState;
  r_pu == r_pu_sig'ramp(trans_time, trans_time);
  v_pu == r_pu*i_pu;

  DetectPDState: process (d_input_inv)
  begin
    if (d_input_inv'event and d_input_inv = '0') then
      r_pd_sig <= r_open;
    elsif (d_input_inv'event and d_input_inv = '1') then
      r_pd_sig <= r_closed;
    end if;
  end process DetectPDState;
  r_pd == r_pd_sig'ramp(trans_time, trans_time);
  v_pd == r_pd*i_pd;

  v_cap*cap == i_cap'integ;

  i_gc == isat*(exp(v_gc/vt) - 1.0);

  i_pc == isat*(exp(v_pc/vt) - 1.0);

end linear;
