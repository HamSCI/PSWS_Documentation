#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 29, 2020
WWV file corruption processing.
Faliure mode is power gets cut off to RasPi and the last buffer write to disk has 
paded the file with null chars.  Then on restart FLDigi starts before the clock 
gets set (usually backwards in time) and then when the system clock sets, its jumps 
forward to the correct time.  THis is the fingerprint of the corruption.  Both are fixed.

@author @jcgibbons N8OBJ
"""
import maidenhead as mh

print('Maidenhead Program')

lat = 41.32191
long = -81.50478

print('Latitude = ', lat)
print('Longitude = ', long)

gridsquare =  mh.to_maiden(lat, long)
print('GridSquare = ', gridsquare)


