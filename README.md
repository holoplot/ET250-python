# Python script to control ET250-3D turntables

## Protocol

This is an implementation of the [protocol described by the vendor](https://drive.google.com/file/d/0BwJWB_u5BPgtZVpTaG9DUlNLTk0/view?usp=sharing).

## Usage

The python script can be called as CLI.

Move the turntable forward by 90 degrees:

`./control.py --address 10.0.0.100 --command forward --degree 90`

Move the turntable backward by 90 degrees:

`./control.py --address 10.0.0.100 --command backward --degree 90`

Move the turntable to its zero position:

`./control.py --address 10.0.0.100 --command zero`

Stop the turntable if it's currently in motion:

`./control.py --address 10.0.0.100 --command stop`

## License

MIT

