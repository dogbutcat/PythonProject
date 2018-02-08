function e(inputStr) {
	var o = inputStr.match(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g);
	if (null === o) {
		var t = inputStr.length;
		t > 30 &&
			(inputStr =
				"" +
				inputStr.substr(0, 10) +
				inputStr.substr(Math.floor(t / 2) - 5, 10) +
				inputStr.substr(-10, 10));
	} else {
		for (
			var e = inputStr.split(/[\uD800-\uDBFF][\uDC00-\uDFFF]/),
				SIndex = 0,
				h = e.length,
				f = [];
			h > SIndex;
			SIndex++
		) {
			if ("" !== e[SIndex]) {
				f.push.apply(f, [...e[SIndex].split("")]);
			}
			if (SIndex !== h - 1) {
				f.push(o[SIndex]);
			}
		}
		var g = f.length;
		g > 30 &&
			(inputStr =
				f.slice(0, 10).join("") +
				f.slice(Math.floor(g / 2) - 5, Math.floor(g / 2) + 5).join("") +
				f.slice(-10).join(""));
	}
	var gtkStr = void 0,
		l = "gtk";
	gtkStr = null !== inner ? inner : (inner = window[l] || "") || "";
	for (
		var d = gtkStr.split("."),
			firstSplit = Number(d[0]) || 0,
			secondSplit = Number(d[1]) || 0,
			S = [],
			SIndex = 0,
			v = 0;
		v < inputStr.length;
		v++
	) {
		var A = inputStr.charCodeAt(v);
		if (128 > A) {
			S[SIndex++] = A;
		} else {
			if (2048 > A) {
				S[SIndex++] = (A >> 6) | 192;
			} else {
				if (
					55296 === (64512 & A) &&
					v + 1 < inputStr.length &&
					56320 === (64512 & inputStr.charCodeAt(v + 1))
				) {
					A = 65536 + ((1023 & A) << 10) + (1023 & inputStr.charCodeAt(++v));
					S[SIndex++] = (A >> 18) | 240;
					S[SIndex++] = ((A >> 12) & 63) | 128;
				} else {
					S[SIndex++] = (A >> 12) | 224;
					S[SIndex++] = ((A >> 6) & 63) | 128;
				}
			}
			S[SIndex++] = (63 & A) | 128;
		}
	}
	for (
		var p = firstSplit,
			F =
				"" +
				String.fromCharCode(43) +
				String.fromCharCode(45) +
				String.fromCharCode(97) +
				("" +
					String.fromCharCode(94) +
					String.fromCharCode(43) +
					String.fromCharCode(54)), //"+-a^+6",
			D =
				"" +
				String.fromCharCode(43) +
				String.fromCharCode(45) +
				String.fromCharCode(51) +
				("" +
					String.fromCharCode(94) +
					String.fromCharCode(43) +
					String.fromCharCode(98)) +
				("" +
					String.fromCharCode(43) +
					String.fromCharCode(45) +
					String.fromCharCode(102)), //"+-3^+b+-f",
			j = 0;
		j < S.length;
		j++
	)
		(p += S[j]), (p = n(p, F));
	return (
		(p = n(p, D)),
		(p ^= secondSplit),
		0 > p && (p = (2147483647 & p) + 2147483648),
		(p %= 1e6),
		p.toString() + "." + (p ^ firstSplit)
	);
}

function n(targetNum, str2) {
	for (var i = 0; i < str2.length - 2; i += 3) {
		var thirdChar = str2.charAt(i + 2);
		if (thirdChar >= "a") {
			// if over 97
			thirdChar = thirdChar.charCodeAt(0) - 87; //10+?
		} else {
			thirdChar = Number(thirdChar);
		}
		// thirdChar is number now
		if ("+" === str2.charAt(i + 1)) {
			// if second char is +
			thirdChar = targetNum >>> thirdChar;
		} else {
			thirdChar = targetNum << thirdChar;
		}
		if ("+" === str2.charAt(i)) {
			targetNum = (targetNum + thirdChar) & 4294967295; // 4294967295 = Math.pow(2,32)-1
		} else {
			targetNum = targetNum ^ thirdChar;
		}
	}
	return targetNum;
}
