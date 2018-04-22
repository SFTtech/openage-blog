Title: Implementing Python-Style Enums in C++
Date: 2018-04-21 23:01
Category: fun
Tags: C++, templates
Authors: zuntrax, mic-e, jj
Summary: the fun journey of implementing proper enums in C++

It has been proven over and over again that we suffer from a severe form of [NIH](https://en.wikipedia.org/wiki/Not_invented_here). Today, we tried to reinvent the wheel once again, but with rockets attached, and tackled the beauty of C++17 by creating a *usable* enum implementation.


The current `openage` enums sometimes produce linker errors on macOS and warnings on other systems:

<details>
 <summary>(`instanciation of enum required here, but no definition is available`)</summary>
 <pre>
...
[ 35%] Building CXX object libopenage/CMakeFiles/libopenage.dir/log/stdout_logsink.cpp.o
In file included from /home/jj/devel/openage/libopenage/log/stdout_logsink.cpp:3:
In file included from /home/jj/devel/openage/libopenage/log/stdout_logsink.h:5:
In file included from /home/jj/devel/openage/libopenage/log/logsink.h:8:
In file included from /home/jj/devel/openage/libopenage/log/level.h:8:
/home/jj/devel/openage/libopenage/log/../util/enum.h:99:17: warning: instantiation of variable 'openage::util::Enum<openage::log::level_properties>::data' required here, but no definition is available [-Wundefined-var-template]
                return &this->data[this->id].second;
                              ^
/home/jj/devel/openage/libopenage/log/stdout_logsink.cpp:16:33: note: in instantiation of member function 'openage::util::Enum<openage::log::level_properties>::operator->' requested here
        std::cout << "\x1b[" << msg.lvl->colorcode << "m" << std::setw(4) << msg.lvl->name << "\x1b[m" " ";
                                       ^
/home/jj/devel/openage/libopenage/log/../util/enum.h:129:19: note: forward declaration of template entity is here
        static data_type data;
                         ^
/home/jj/devel/openage/libopenage/log/../util/enum.h:99:17: note: add an explicit instantiation declaration to suppress this warning if 'openage::util::Enum<openage::log::level_properties>::data' is explicitly instantiated in another translation unit
                return &this->data[this->id].second;
                              ^
1 warning generated.
...
 </pre>
</details>

We tried getting rid of that warning several times, but that always led into a deep rabbit hole of linker errors. Now we were fed up and decided to get rid of our [old enum implementation](https://github.com/SFTtech/openage/blob/faae03bcbfd6685b2db8bd80a63b5762bcfc490e/libopenage/util/enum.h).

## Why?

But why this own enum implementation?

* Usage exactly like the `enum class`
* Have a string representation of each enum value
* Allow member methods for the enum type
* Everything at compile time and accross TUs without funny `extern` definitions

After some experiments, we implemented it with a wrapper class (`EnumValueContainer`) which has implicit conversions to the `EnumValue` type. The actual enum values are `constexpr static` members of a subclass of `EnumValue`. We need this in order to use `LogLevel` for both containing the all possible enum values, being the type for the enum like an `enum class` name, and using it as non-const type that references to one of the possible values.

This way, the container can store a reference to its static member, i.e. a handle to a enum value like you know from `enum class`!

The remaining problem was member methods, especially because the "container" class type should also be usable a enum-value type.
To achieve this, we had the idea of using a mixin class `LogLevelMethods` with [CRTP](https://en.wikipedia.org/wiki/Curiously_recurring_template_pattern). This is what we came up with:

#### enum.h
``` cpp
#pragma once

#include <iostream>
#include <typeinfo>
#include <type_traits>
#include <cxxabi.h>

template<typename DerivedType, typename NumericType=int>
struct EnumValue {
	// enum values cannot be copied
	EnumValue(const EnumValue &other) = delete;
	EnumValue &operator =(const EnumValue &other) = delete;

	// enum values are equal if the pointers are equal.
	constexpr bool operator ==(const DerivedType &other) const {
		return (this == &other);
	}

	/* SNIP */

	friend std::ostream &operator <<(std::ostream &os, const DerivedType &arg) {
		int status;
		os << abi::__cxa_demangle(typeid(DerivedType).name(), 0, 0, &status) << "::" << arg.name;
		return os;
	}

	const char *name;
	NumericType numeric;
};

template<typename DerivedType>
struct EnumValueContainer {
	using this_type = EnumValueContainer<DerivedType>;

	const DerivedType &value;

	constexpr EnumValueContainer(const DerivedType &value) : value{value} {}

	// implicit conversion operator!
	constexpr operator const DerivedType &() const {
		return this->value;
	}

	constexpr EnumValueContainer &operator =(const DerivedType &value) {
		this->value = value;
	}

	constexpr bool operator ==(const this_type &other) const {
		return (this->value == other.value);
	}

	/* SNIP */

	friend std::ostream &operator <<(std::ostream &os, const this_type &arg) {
		os << arg.value;
		return os;
	}
};


struct NOVAL {};
struct VAL {};


template <typename T, typename novalue, typename ET=void>
struct EnumMethods {
	template <typename X=novalue>
	typename std::enable_if<std::is_same<X, NOVAL>::value, const T*>::type
	get_this() const {
		return static_cast<const T*>(this);
	};

	template <typename X=novalue>
	typename std::enable_if<std::is_same<X, VAL>::value, const T*>::type
	get_this() const {
		return static_cast<const T*>(&(static_cast<const ET*>(this))->value);
	};
};


```

#### loglevel.h
``` cpp
#pragma once

#include "enum.h"


template <typename T, typename novalue, typename ET=void>
struct LogLevelMethods : EnumMethods<T, novalue, ET> {
	void foo() const {
		std::cout << "foo is " << this->get_this()->name << std::endl;
	}
};


/** Here, new member values for each enum value can be added */
struct LogLevelValue : EnumValue<LogLevelValue>, LogLevelMethods<LogLevelValue, NOVAL> {
	const char *color_code;
};


/** Usage of the first design attempt for the new enum */
struct LogLevel : EnumValueContainer<LogLevelValue>, LogLevelMethods<LogLevelValue, VAL, LogLevel> {
	using EnumValueContainer<LogLevelValue>::EnumValueContainer;

	static constexpr LogLevelValue debug = {{"debug", 10}, {}, "31;1"};
	static constexpr LogLevelValue info = {{"info", 20}, {}, "32"};
};
```

Thus, it is now possible to to this:
``` cpp
LogLevel a = LogLevel::info;  // store a handle to the static constexpr member!
a.foo();                      // call the enum "member" method!
LogLevel::info.foo();         // same, but without the LogLevel wrapper!
```

But why does that work?

The `=` assignment uses the implicit conversion from `LogLevelValue` to `LogLevel`. The latter stores a reference to `LogLevelValue`.

The `a.foo()` call is even more obscure: The magic with `LogLevelMethods` effectively "redirects" the `operator .` from `LogLevel` to `LogLevelValue` through `LogLevelMethods` via `EnumMethods`.

`EnumMethods` adds the `foo` method to both the `LogLevel` container and each `LogLevelValue` directly, and can convert the `this` pointer accordingly to reach the per-enum-value data. If we kept this, we probably would have added macros to simplify the template shenanigans in the declarations of `LogLevelValue` and `LogLevel`.

Containing almost standard-library-levels of template magic, we didn't exactly want to commit this to the repo.


## Improvements

The **much easier variant**, which works without a redirect/"overload" of the `operator .` is to just use `operator ->` instead, which can actually be overloaded without hacks:

``` cpp
struct EnumValueContainer {
	/* ... */
	constexpr const DerivedType *operator ->() const {
		return &(this->value);
	}
	/* ... */
}

struct LogLevelValue : EnumValue<LogLevelValue> {
	const char *color_code;
	// of course, more members and functions could be added here

	void foo() const {
		std::cout << "foo: " << this->name << std::endl;
	}
}

/** Usage of the "final" design for our new enum */
struct LogLevel : EnumValueContainer<LogLevelValue> {
	using EnumValueContainer<LogLevelValue>::EnumValueContainer;

	static constexpr LogLevelValue debug = {{"debug", 10}, "31;1"};
	static constexpr LogLevelValue info = {{"info", 20}, "32"};
};
```

Now, we can just call it with `->`:

``` cpp
int main() {
	LogLevel lvl = LogLevel::debug;
	lvl->foo();
	return 0;
}
```

Mind that all this **only works with C++17**.

<details>
 <summary>Here is the full code for our new enum (GPLv3 or later):</summary>

#### Enum definition:
``` cpp
// Copyright 2018 the openage authors, GPLv3 or later.
#pragma once

#include <iostream>
#include <typeinfo>
#include <cxxabi.h>


template<typename DerivedType, typename NumericType=int>
struct EnumValue {
	// enum values cannot be copied
	EnumValue(const EnumValue &other) = delete;
	EnumValue &operator =(const EnumValue &other) = delete;

	// enum values are equal if the pointers are equal.
	constexpr bool operator ==(const DerivedType &other) const {
		return (this == &other);
	}

	constexpr bool operator !=(const DerivedType &other) const {
		return !(*this == other);
	}

	constexpr bool operator <=(const DerivedType &other) const {
		return this->numeric <= other.numeric;
	}

	constexpr bool operator <(const DerivedType &other) const {
		return this->numeric < other.numeric;
	}

	constexpr bool operator >=(const DerivedType &other) const {
		return this->numeric >= other.numeric;
	}

	constexpr bool operator >(const DerivedType &other) const {
		return this->numeric > other.numeric;
	}

	friend std::ostream &operator <<(std::ostream &os, const DerivedType &arg) {
		int status;
		os << abi::__cxa_demangle(typeid(DerivedType).name(), 0, 0, &status) << "::" << arg.name;
		return os;
	}

	const char *name;
	NumericType numeric;
};


template<typename DerivedType>
struct EnumValueContainer {
	using this_type = EnumValueContainer<DerivedType>;

	const DerivedType &value;

	constexpr EnumValueContainer(const DerivedType &value) : value{value} {}

	constexpr operator const DerivedType &() const {
		return this->value;
	}

	constexpr EnumValueContainer &operator =(const DerivedType &value) {
		this->value = value;
	}

	constexpr const DerivedType *operator ->() const {
		return &(this->value);
	}

	constexpr bool operator ==(const this_type &other) const {
		return (this->value == other.value);
	}

	constexpr bool operator !=(const this_type &other) const {
		return (this->value != other.value);
	}

	constexpr bool operator <=(const this_type &other) const {
		return this->value <= other.value;
	}

	constexpr bool operator <(const this_type &other) const {
		return this->value < other.value;
	}

	constexpr bool operator >=(const this_type &other) const {
		return this->value >= other.value;
	}

	constexpr bool operator >(const this_type &other) const {
		return this->value > other.value;
	}

	friend std::ostream &operator <<(std::ostream &os, const this_type &arg) {
		os << arg.value;
		return os;
	}
};
```

#### Usage:
``` cpp
#pragma once

#include "enum.h"


struct LogLevelValue : EnumValue<LogLevelValue> {
	const char *color_code;

	void bar() const {
		std::cout << "bar is " << this->name << " and " << this->color_code << std::endl;
	}
};


struct LogLevel : EnumValueContainer<LogLevelValue> {
	using EnumValueContainer<LogLevelValue>::EnumValueContainer;

	static constexpr LogLevelValue debug = {{"debug", 10}, "31;1"};
	static constexpr LogLevelValue info = {{"info", 20}, "32"};
};

int main() {
	LogLevel l = LogLevel::debug;
	std::cout << l << " => " << l->bar() << std::endl;
	std::cout << (LogLevel::debug < LogLevel::info) << std::endl;

	return 0;
}
```

</details>

Oh C++, such an adventure game.
