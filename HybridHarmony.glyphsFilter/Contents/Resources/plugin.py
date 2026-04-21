# encoding: utf-8

###########################################################################################################
#
#	Filter without dialog Plugin
#
#	Hybrid Harmony - G2 harmonization with minimal shape change
#
#	Derived from:
#	- Green Harmony by Alex Slobzheninov (@slobzheninov)
#	  https://github.com/slobzheninov/GreenHarmony
#	- Grey Harmony by Rainer Erich Scheichelbauer (@mekkablue)
#	  https://github.com/mekkablue/GreyHarmony
#	- Both based on algorithm by Simon Cozens (@simoncozens)
#	  https://gist.github.com/simoncozens/3c5d304ae2c14894393c6284df91be5b
#	- Template code by Georg Seifert (@schriftgestalt) and Jan Gerner (@yanone)
#
#	Copyright 2026 - Derived work under Apache License 2.0
#
#	Licensed under the Apache License, Version 2.0 (the "License");
#	you may not use this file except in compliance with the License.
#	You may obtain a copy of the License at
#
#	http://www.apache.org/licenses/LICENSE-2.0
#
###########################################################################################################

from __future__ import division, print_function, unicode_literals
import objc
from GlyphsApp import Glyphs, GSPath, subtractPoints, addPoints, CURVE, OFFCURVE
from GlyphsApp.plugins import FilterWithoutDialog
from math import sqrt
from Foundation import NSPoint
from AppKit import NSControlKeyMask, NSShiftKeyMask, NSAlternateKeyMask, NSEvent


def getIntersection(x1, y1, x2, y2, x3, y3, x4, y4):
	"""
	Calculate intersection point of two lines.
	Line 1: (x1,y1) -> (x2,y2)
	Line 2: (x3,y3) -> (x4,y4)
	Returns (px, py) or None if lines are parallel.
	"""
	denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
	if abs(denominator) < 1e-10:  # Lines are parallel or nearly parallel
		return None
	
	px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denominator
	py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denominator
	return px, py


def getDist(a, b):
	"""Calculate Euclidean distance between two points."""
	return sqrt((b.x - a.x)**2 + (b.y - a.y)**2)


def remap(oldValue, oldMin, oldMax, newMin, newMax):
	"""Linear interpolation/extrapolation from one range to another."""
	try:
		oldRange = (oldMax - oldMin)
		if abs(oldRange) < 1e-10:
			return None
		newRange = (newMax - newMin)
		newValue = (((oldValue - oldMin) * newRange) / oldRange) + newMin
		return newValue
	except:
		return None


def harmonizeNode(node, alpha=0.65):
	"""
	Apply hybrid G2 harmonization to a smooth curve node.
	
	Args:
		node: The on-curve node to harmonize
		alpha: Blend factor (0.0 = Grey only [move handles], 1.0 = Green only [move node])
	
	Returns:
		True if harmonization was applied, False if conditions were not met.
	"""
	# Validate node type and smoothness
	if node.type != CURVE or not node.smooth:
		return False
	
	# Get adjacent nodes
	N = node.nextNode  # Next handle
	P = node.prevNode  # Previous handle
	
	if not N or not P:
		return False
	
	if N.type != OFFCURVE or P.type != OFFCURVE:
		return False
	
	NN = N.nextNode  # Next on-curve
	PP = P.prevNode  # Previous on-curve
	
	if not NN or not PP:
		return False
	
	# Find intersection of lines created by off-curves
	intersection = getIntersection(N.x, N.y, NN.x, NN.y, P.x, P.y, PP.x, PP.y)
	
	if intersection is None:
		return False  # Parallel lines, cannot compute harmonization
	
	xIntersect, yIntersect = intersection
	intersectionPoint = NSPoint(xIntersect, yIntersect)
	
	# Calculate distance ratios for G2 continuity
	distNN_N = getDist(NN, N)
	distN_I = getDist(N, intersectionPoint)
	distI_P = getDist(intersectionPoint, P)
	distP_PP = getDist(P, PP)
	
	# Guard against division by zero
	if distN_I < 1e-10 or distP_PP < 1e-10:
		return False
	
	r0 = distNN_N / distN_I
	r1 = distI_P / distP_PP
	
	if r0 < 0 or r1 < 0:
		return False  # Invalid geometry
	
	ratio = sqrt(r0 * r1)
	t = ratio / (ratio + 1)
	
	# Calculate target position for Green Harmony (moving the on-curve node)
	targetX = remap(t, 0, 1, N.x, P.x)
	targetY = remap(t, 0, 1, N.y, P.y)
	
	if targetX is None or targetY is None:
		return False
	
	targetPosition = NSPoint(targetX, targetY)
	
	# Calculate displacement vector
	deltaX = targetX - node.x
	deltaY = targetY - node.y
	delta = NSPoint(deltaX, deltaY)
	
	# Apply blended movement
	# alpha = 1.0: move only the on-curve node (Green Harmony)
	# alpha = 0.0: move only the handles (Grey Harmony)
	# 0 < alpha < 1: blend both approaches
	
	# Move on-curve node by alpha proportion
	node.x += deltaX * alpha
	node.y += deltaY * alpha

	# Move handles by (1 - alpha) proportion in opposite direction to compensate
	# This maintains relative curve shape when node only partially moves
	handleDeltaX = -deltaX * (1.0 - alpha)
	handleDeltaY = -deltaY * (1.0 - alpha)

	N.x += handleDeltaX
	N.y += handleDeltaY
	P.x += handleDeltaX
	P.y += handleDeltaY
	
	return True


class HybridHarmony(FilterWithoutDialog):
	
	@objc.python_method
	def settings(self):
		self.menuName = Glyphs.localize({
			'en': 'Hybrid Harmony',
			'de': 'Hybride Harmonie',
			'fr': 'Harmonie hybride',
			'es': 'Armonía híbrida',
			'it': 'Armonia ibrida',
			'cs': 'Hybridní harmonie',
			'pt': 'Harmonia híbrida',
			'ru': 'Гибридная гармония',
			'jp': 'ハイブリッド調和',
			'ko': '하이브리드 조화',
			'zh': '🔀混合和谐',
		})
		
		# Default keyboard shortcut: Ctrl-Shift-H
		self.keyboardShortcut = 'h'
		self.keyboardShortcutModifier = NSControlKeyMask | NSShiftKeyMask
	
	@objc.python_method
	def filter(self, layer, inEditView, customParameters):
		"""
		Main filter method called by Glyphs.
		
		Custom parameters supported:
		- alpha: blend factor 0.0-1.0 (default 0.5)
		- allLayers: apply to compatible layers (default False)
		"""
		# Parse custom parameters
		alpha = 0.65  # Default: equal blend of Green and Grey
		applyToAllLayers = False
		
		if customParameters:
			if 'alpha' in customParameters:
				try:
					alpha = float(customParameters['alpha'])
					alpha = max(0.0, min(1.0, alpha))  # Clamp to [0, 1]
				except:
					pass
			
			if 'allLayers' in customParameters:
				applyToAllLayers = bool(customParameters.get('allLayers'))
		
		# Check for modifier keys in edit view
		if inEditView:
			keysPressed = NSEvent.modifierFlags()
			
			# Shift: Green-only mode (alpha = 1.0)
			if keysPressed & NSShiftKeyMask == NSShiftKeyMask:
				alpha = 1.0
			
			# Alt/Option: Grey-only mode (alpha = 0.0)
			elif keysPressed & NSAlternateKeyMask == NSAlternateKeyMask:
				alpha = 0.0
			
			# Check if Option key is pressed for all-layers mode
			if keysPressed & NSAlternateKeyMask == NSAlternateKeyMask:
				applyToAllLayers = True
		
		# Determine which nodes to process
		selectionCounts = bool(inEditView) and bool(layer.selection)
		
		# Process current layer
		self._processLayer(layer, selectionCounts, alpha)
		
		# Optionally process compatible layers
		if applyToAllLayers and layer.parent:
			currentCompareString = layer.compareString()
			for otherLayer in layer.parent.layers:
				if otherLayer is not layer and otherLayer.compareString() == currentCompareString:
					self._processLayer(otherLayer, False, alpha)  # Process all nodes in compatible layers
	
	@objc.python_method
	def _processLayer(self, layer, selectionCounts, alpha):
		"""Process nodes in a single layer."""
		if not layer.shapes:
			return
		
		for shape in layer.shapes:
			if not isinstance(shape, GSPath):
				continue
			
			for node in shape.nodes:
				# Skip if selection exists and this node is not selected
				if selectionCounts and node not in layer.selection:
					continue
				
				# Apply harmonization
				harmonizeNode(node, alpha)
	
	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
