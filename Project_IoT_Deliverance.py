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

vlPH['asam'] = fuzz.trapmf(vlPH.universe, [0, 0, 4, 6.5])
vlPH['netral'] = fuzz.trapmf(vlPH.universe, [6, 7, 8, 9])
vlPH['basa'] = fuzz.trapmf(vlPH.universe, [7.5, 8, 14, 14])

vlTDS['rendah'] = fuzz.trapmf(vlTDS.universe, [0, 0, 200, 500])
vlTDS['tinggi'] = fuzz.trapmf(vlTDS.universe, [300, 500, 2000, 2000])

vlTurbidity['rendah'] = fuzz.trapmf(vlTurbidity.universe, [0, 0, 2, 5])
vlTurbidity['tinggi'] = fuzz.trapmf(vlTurbidity.universe, [3, 5, 10, 10])

vlDrinkable['tidak'] = fuzz.trapmf(vlDrinkable.universe, [0, 0, 30, 50])
vlDrinkable['sedang'] = fuzz.trapmf(vlDrinkable.universe, [40, 50, 70, 80])
vlDrinkable['ya'] = fuzz.trapmf(vlDrinkable.universe, [70, 80, 100, 100])

# Rule
rule1 = ctrl.Rule(vlPH['asam'] | vlTDS['tinggi'] | vlTurbidity['tinggi'], vlDrinkable['tidak'])
rule2 = ctrl.Rule(vlPH['netral'] & vlTDS['rendah'] & vlTurbidity['rendah'], vlDrinkable['ya'])
rule3 = ctrl.Rule(vlPH['basa'] & vlTDS['rendah'] & vlTurbidity['tinggi'], vlDrinkable['tidak'])
rule4 = ctrl.Rule(vlPH['asam'] & vlTDS['rendah'] & vlTurbidity['rendah'], vlDrinkable['sedang'])
rule5 = ctrl.Rule(vlPH['netral'] | vlTDS['tinggi'] | vlTurbidity['rendah'], vlDrinkable['sedang'])


set_air_minum = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5])
air_minum = ctrl.ControlSystemSimulation(set_air_minum)

while True:
    air_minum.input['ph'] = get_ph()
    air_minum.input['tds'] = get_tds()
    air_minum.input['turbidity'] = get_turbidity()

    air_minum.compute()

    drinkability = air_minum.output['drinkable']

    print('Nilai PH:', get_ph())
    print('Nilai TDS:', get_tds())
    print('Nilai Turbidity:', get_turbidity())
    print('Kualitas Minum:', drinkability)
    if drinkability >= 70:
        print('AIR AMAN UNTUK DIMINUM')
    elif drinkability >= 50:
        print('SEBAIKNYA JANGAN DIMINUM')
    else:
        print('AIR BERBAHAYA')

    time.sleep(0.05)
