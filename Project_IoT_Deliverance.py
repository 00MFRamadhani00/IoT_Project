#import pyfirmata
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)

pinPH = 4
pinTDS = 5
pinTBDT = 26


GPIO.setup(pinPH, GPIO.IN)
GPIO.setup(pinTDS, GPIO.IN)
GPIO.setup(pinTBDT, GPIO.IN)

def get_tds():
    tds = GPIO.input(pinTDS)
    return tds

def get_ph():
    ph = GPIO.input(pinPH)
    return ph

def get_turbidity():
    turbidity = GPIO.input(pinTBDT)
    return turbidity

vlPH = ctrl.Antecedent(np.arange(0, 14, 0.1), 'ph')
vlTDS = ctrl.Antecedent(np.arange(0, 2000, 1), 'tds')
vlTurbidity = ctrl.Antecedent(np.arange(0, 10, 0.1), 'turbidity')
vlDrinkable = ctrl.Antecedent(np.arange(0, 101, 1), 'drinkable')

vlPH['asam'] = fuzz.trimf(vlPH.universe, [0, 0, 6.5])
vlPH['netral'] = fuzz.trimf(vlPH.universe, [6.5, 7, 8])
vlPH['basa'] = fuzz.trimf(vlPH.universe, [7, 8, 14])

vlTDS['rendah'] = fuzz.trimf(vlTDS.universe, [0, 0, 500])
vlTDS['tinggi'] = fuzz.trimf(vlTDS.universe, [0, 500, 2000])

vlTurbidity['rendah'] = fuzz.trimf(vlTurbidity.universe, [0, 0, 5])
vlTurbidity['tinggi'] = fuzz.trimf(vlTurbidity.universe, [0, 5, 10])

vlDrinkable['tidak'] = fuzz.trimf(vlDrinkable.universe, [0, 0, 50])
vlDrinkable['ya'] = fuzz.trimf(vlDrinkable.universe, [0, 50, 100])

# Rule
rule1 = ctrl.Rule(vlPH['asam'] | vlTDS['tinggi'] | vlTurbidity['tinggi'], vlDrinkable['tidak'])
rule2 = ctrl.Rule(vlPH['netral'] | vlTDS['rendah'] | vlTurbidity['rendah'], vlDrinkable['ya'])

set_air_minum = ctrl.ControlSystem([rule1, rule2])
air_minum = ctrl.ControlSystemSimulation(set_air_minum)

air_minum.input['ph'] = get_ph()
air_minum.input['tds'] = get_tds()
air_minum.input['turbidity'] =get_turbidity()

air_minum.compute()

drinkability = air_minum.output['drinkable']

while True:
    print('Nilai PH:', get_ph())
    print('Nilai TDS:', get_tds())
    print('Nilai Turbidity:', get_turbidity())
    print('Kualitas Minum:', drinkability)
    if drinkability >= 70:
        print('AIR AMAN UNTUK DIMINUM')
    elif drinkability >=50:
        print('SEBAIKNYA JANGAN DIMINUM')
    else:
        print('AIR BERBAHAYA')
    time.sleep(0.05)
