"""
"""

import os
import sys
import platform
import UserDict
import itertools
import re


__NULL__ = "__NULL__"
_VAR_SUB = {"windows":"\%(.*?)\%", "linux":"\${(.*?)}", "osx":"\${(.*?)}"}


class UndefinedVariableError(Exception):
	"""
	Raised when an undefined environement variable is queried.
	"""
	def __init__(self, key):
		"""
		"""
		super(UndefinedVariableError, self).__init__("Undefined Environment Varialbe: %s" % key)

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

	def normalize(self, val):
		"""
		Normalize a value by collapsing redundant separators. If a leading separator exists, it is
		left intact.
		@param val A string value to normalize
		@returns A normalized value
		"""
		if not isinstance(val, basestring):
			raise TypeError("Value must be of type str, not %s" % type(val).__name__)

		vals = val.split(os.pathsep)
		vals = [ x for x in vals if x]
		vals = os.pathsep.join(vals)
		if val.startswith(os.pathsep):
			vals = "%s%s" % (os.pathsep, vals)
		return vals

	def splitvals(self, val):
		"""
		Split the val into a list based on the os.pathsep
		@param val The string or list value to split.
		@returns List of values
		"""
		if hasattr(val, "__iter__"):
			return list(itertools.chain.from_iterable([ self.splitvals(x) \
																for x in val ]))
		if isinstance(val, basestring):
			normalized = self.normalize(val)
			return normalized.split(os.pathsep)

		raise TypeError("Environment values must be of type str, not %s" % type(val).__name__)

	def set(self, key, val):
		"""
		Set the value of key in the environment
		@param key The environment key.
		@param val The environment value.
		"""
		if val:
			vals = self.splitvals(val)

			#check if any of the vars are appending or prepending
			appending = len([ v for v in vals if v.startswith("+")]) > 0

			#if any of the vars are appending or prepending use the existing env vars
			if appending:
				data_vals = self.data.get(key, None)
				if data_vals is None:
					data_vals = []
			#if not appending or prepending, overwrite the existing env vars
			else:
				data_vals = []

			for val in vals:
				#if prepending
				if val.startswith("++"):
					data_vals.insert(0, val.strip("+"))
				else:
					data_vals.append(val.strip("+"))
			self.data[key] = data_vals
		else:
			self.data[key] = []

	def get(self, key, default=__NULL__):
		"""
		Get the value of the specified environment key.
		@param key The enviornment variable to return the value of.
		@param default A default value to return if the key does not exist.
		@returns String value
		"""
		val = self.data.get(key, __NULL__)

		if val == __NULL__:
			if default == __NULL__:
				raise UndefinedVariableError(key)
			elif default is None:
				return None
			val = self.splitvals(default)

		#no values, return and empty string
		if not val:
			return ""

		#join the values on the path separator
		return os.pathsep.join(val)

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

	def list(self, out=None):
		"""
		List all expanded envioronment variables in the format: <key>=<value>
		One key/value pair per line.
		@param out A writer object to write the listing to. out can be any object with a write()
		method.
		@returns A string listing of all expanded environment variables.
		"""
		key_values = []
		for k in self.data:
			key_values.append("%s=%s" % (k, self.get(k)))
		key_values = "\n".join(sorted(key_values))
		if out:
			out.write(key_values)
		return key_values

	def expandvars(self, var_string, env=None, var_sub_platform=None):
		"""
		"""
		var_sub_platform = var_sub_platform or platform.system()
		var_sub = _VAR_SUB[var_sub_platform.lower()]

		for match in re.finditer(var_sub, var_string):
			var = match.group(1)
			if env:
				val = env.get(var, None)
			else:
				val = self.get(var, None)
			if val is not None:
				var_string = re.sub("\${%s}" % var, val, var_string)
		return var_string

	def _build_dependencies(self):
		"""
		Run through all vars and parse out any var dependencies.
		@returns A dict in the format {var:[dependency, ...].
		"""
		dependencies = {}
		var_sub = _VAR_SUB[platform.system().lower()]
		for key in self.data:
			val = self.get(key)
			if key not in dependencies:
				dependencies[key] = []

			for match in re.finditer(var_sub, val):

				dependency = match.group(1)
				if dependency not in dependencies[key]:
					dependencies[key].append(dependency)
		return dependencies

	def _sort_dependencies(self):
		"""
		Performa a topological sort on the env variable dependencies.
		@returns A two-tuple. The first element containing a list of sorted vars,
		the second, a dict of vars which are causing a cycles and their corresponding dependencies.
		"""
		dependencies = self._build_dependencies()

		sorted_deps = []
		sort_queue = []
		for key, vals in dependencies.items():
			if not vals:
				sort_queue.append(key)
				dependencies.pop(key)

		while sort_queue:
			#pop a sort item from the sort queue
			sort_item = sort_queue.pop()
			#append it to the sorted list
			sorted_deps.append(sort_item)

			#for key and vals in remaining dependencies
			for key, vals in dependencies.items():
				#if the current sort item is in the list of dependencies
				if sort_item in vals:
					#remote it
					vals.remove(sort_item)
					#if there are no more dependencies
					if len(vals) == 0:
						#add the key to the list of sort items
						sort_queue.append(key)

		cycles = {}
		for key, vals in dependencies.items():
			if vals:
				cycles[key] = vals

		return sorted_deps, cycles

	def flatten(self, var_sub_platform=None):
		"""
		Return a new Environment with all vars substitution expanded.
		@returns An Environment object.
		"""
		sorted_keys, cycles = self._sort_dependencies()
		baked_env = {}

		if cycles:
			raise Exception("Unable to flatten list. Possibly due to a missing dependency "\
				 "or dependency cycle(s): %s" % cycles)

		for key in sorted_keys:
			val = self.get(key)
			val = self.expandvars(val, env=baked_env, var_sub_platform=var_sub_platform)
			baked_env[key] = val

		return self.__class__(env=baked_env)

	def __setitem__(self, key, val):
		"""
		"""
		self.set(key, val)

	def __getitem__(self, key):
		"""
		"""
		return self.get(key)











