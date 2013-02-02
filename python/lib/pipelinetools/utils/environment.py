"""
"""

import os
import sys
import UserDict
import itertools

class append(object):
	"""
	"""
	def __init__(self, val):
		self.val = val

class prepend(object):
	"""
	"""
	def __init__(self, val):
		self.val = val

class Environment(UserDict.IterableUserDict):
	"""
	Class that allows for easy manipulation of an OS-environment like dictionary.
	"""
	def __init__(self, env=None):
		"""		
		If env is provided environment is initialized with it's contents. 
		@param env Initial values for the environment. This can be an exixting
		Environment class or a dictionary. If None, the environment is initialized
		with the contents of os.environ
		"""		
		UserDict.IterableUserDict.__init__(self)

		if isinstance(env, Environment):
			self.data = env.data.copy()
		else:
			if env is None:
				init_data = os.environ
			else:
				if not isinstance(env, dict):
					raise ValueError("Value of 'env' must be a dict or None")
				init_data = env.copy()
			for key, val in init_data.items():
				self.set(key, val)

	def splitvals(self, val):
		"""
		Split the val into a list based on the os.pathsep
        @param val The string or list value to split.        
        @returns List of values
		"""		
		if isinstance(val, (list, tuple)):						
			return list(itertools.chain.from_iterable([ self.splitvals(x) \
																for x in val ]))
		return val.strip(os.pathsep).split(os.pathsep)

	def set(self, key, val):
		"""
		Set the value of key in the environment
        @param key The environment key.        
        @param val The environment value.
		"""		
		if isinstance(val, append):
			self.append(key, val.val)
		elif isinstance(val, prepend):
			self.prepend(key, val.val)
		else:
			if val:			
				self.data[key] = self.splitvals(val)
			else:
				self.data[key] = []

	def get(self, key, default=None):
		"""
		Get the value of the specified environment key.
        @param key The enviornment variable to return the value of.
        @param default A default value to return if the key does not exist.        
        @returns String value
		"""
		val = self.data.get(key, default)
		if val is None:
			return default
		if len(val) > 1:			
			return os.pathsep.join(val)
		return val[0]

	def append(self, key, val):
		"""
		Append an existing environment variable with a value.
        @param key The environment variable.        
        @param val The value to append.       
		"""
		if key in self.data:						
			self.data[key].extend(self.splitvals(val))
		else:
			self.set(key, val)

	def prepend(self, key, val):
		"""
		Prepend an existing environment variable with a value.
        @param key The environment variable.        
        @param val The value to prepend.        
		"""
		if key in self.data:						
			self.data[key].insert(0, *self.splitvals(val))
		else:
			self.set(key, val)
		

	def __setitem__(self, key, val):
		"""
		"""
		self.set(key, val)

	def __getitem__(self, key):
		"""
		"""
		return self.get(key)

	
		

	






