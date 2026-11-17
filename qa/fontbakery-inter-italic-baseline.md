## FontBakery report

fontbakery version: 1.1.0







## Check results



<details><summary>[11] InterVariable-Italic.ttf</summary>
<div>
<details>
    <summary>🔥 <b>FAIL</b> Check base characters have non-zero advance width. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#base-has-width">base_has_width</a></summary>
    <div>







* 🔥 **FAIL** <p>The following glyphs had zero advance width:
- uni0488 (U+0488)</p>
<pre><code>- uni0489 (U+0489)
</code></pre>
 [code: zero-width-bases]



</div>
</details>

<details>
    <summary>🔥 <b>FAIL</b> Ensure the font supports case swapping for all its glyphs. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#case-mapping">case_mapping</a></summary>
    <div>







* 🔥 **FAIL** <p>The following glyphs lack their case-swapping counterparts:</p>
<table>
<thead>
<tr>
<th align="left">Glyph present in the font</th>
<th align="left">Missing case-swapping counterpart</th>
</tr>
</thead>
<tbody>
<tr>
<td align="left">U+019B: LATIN SMALL LETTER LAMBDA WITH STROKE</td>
<td align="left">U+A7DC: LATIN CAPITAL LETTER LAMBDA WITH STROKE</td>
</tr>
<tr>
<td align="left">U+01C6: LATIN SMALL LETTER DZ WITH CARON</td>
<td align="left">U+01C4: LATIN CAPITAL LETTER DZ WITH CARON</td>
</tr>
<tr>
<td align="left">U+023A: LATIN CAPITAL LETTER A WITH STROKE</td>
<td align="left">U+2C65: LATIN SMALL LETTER A WITH STROKE</td>
</tr>
<tr>
<td align="left">U+023E: LATIN CAPITAL LETTER T WITH DIAGONAL STROKE</td>
<td align="left">U+2C66: LATIN SMALL LETTER T WITH DIAGONAL STROKE</td>
</tr>
<tr>
<td align="left">U+0264: LATIN SMALL LETTER RAMS HORN</td>
<td align="left">U+A7CB: LATIN CAPITAL LETTER RAMS HORN</td>
</tr>
<tr>
<td align="left">U+0265: LATIN SMALL LETTER TURNED H</td>
<td align="left">U+A78D: LATIN CAPITAL LETTER TURNED H</td>
</tr>
<tr>
<td align="left">U+0266: LATIN SMALL LETTER H WITH HOOK</td>
<td align="left">U+A7AA: LATIN CAPITAL LETTER H WITH HOOK</td>
</tr>
<tr>
<td align="left">U+026A: LATIN LETTER SMALL CAPITAL I</td>
<td align="left">U+A7AE: LATIN CAPITAL LETTER SMALL CAPITAL I</td>
</tr>
<tr>
<td align="left">U+026C: LATIN SMALL LETTER L WITH BELT</td>
<td align="left">U+A7AD: LATIN CAPITAL LETTER L WITH BELT</td>
</tr>
<tr>
<td align="left">U+029D: LATIN SMALL LETTER J WITH CROSSED-TAIL</td>
<td align="left">U+A7B2: LATIN CAPITAL LETTER J WITH CROSSED-TAIL</td>
</tr>
<tr>
<td align="left">U+0376: GREEK CAPITAL LETTER PAMPHYLIAN DIGAMMA</td>
<td align="left">U+0377: GREEK SMALL LETTER PAMPHYLIAN DIGAMMA</td>
</tr>
<tr>
<td align="left">U+03FA: GREEK CAPITAL LETTER SAN</td>
<td align="left">U+03FB: GREEK SMALL LETTER SAN</td>
</tr>
<tr>
<td align="left">U+052F: CYRILLIC SMALL LETTER EL WITH DESCENDER</td>
<td align="left">U+052E: CYRILLIC CAPITAL LETTER EL WITH DESCENDER</td>
</tr>
<tr>
<td align="left">U+2132: TURNED CAPITAL F</td>
<td align="left">U+214E: TURNED SMALL F</td>
</tr>
</tbody>
</table>
 [code: missing-case-counterparts]



</div>
</details>

<details>
    <summary>🔥 <b>FAIL</b> Checking OS/2 usWinAscent & usWinDescent. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#family-win-ascent-and-descent">family/win_ascent_and_descent</a></summary>
    <div>







* 🔥 **FAIL** <p>OS/2.usWinAscent value should be equal or greater than 2269, but got 1984 instead</p>
 [code: ascent]



* 🔥 **FAIL** <p>OS/2.usWinDescent value should be equal or greater than 660, but got 494 instead</p>
 [code: descent]



</div>
</details>

<details>
    <summary>🔥 <b>FAIL</b> Combined length of family and style must not exceed 31 characters. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#name-family-and-style-max-length">name/family_and_style_max_length</a></summary>
    <div>







* 🔥 **FAIL** <p>Name ID 1 'Inter Variable' plus STAT table style combination 'Display ExtraLight' exceeds 31 characters (the combination is 33 characters).</p>
<p>This has been found to cause a fallback font to appear for some accented letters, as well as in some scripts such as Thai, in Microsoft Word on Windows 10 and 11. It can also lead to names which are truncated in the Microsoft Word font menu.</p>
 [code: familyname-plus-stat-entries-too-long]



* 🔥 **FAIL** <p>Name ID 1 'Inter Variable' plus STAT table style combination 'Display ExtraBold' exceeds 31 characters (the combination is 32 characters).</p>
<p>This has been found to cause a fallback font to appear for some accented letters, as well as in some scripts such as Thai, in Microsoft Word on Windows 10 and 11. It can also lead to names which are truncated in the Microsoft Word font menu.</p>
 [code: familyname-plus-stat-entries-too-long]



</div>
</details>

<details>
    <summary>🔥 <b>FAIL</b> Ensure font doesn't have Mac name table entries (platform=1). <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#no-mac-entries">no_mac_entries</a></summary>
    <div>







* 🔥 **FAIL** <p>Please remove name ID 4</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 6</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 25</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 256</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 257</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 258</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 259</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 260</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 261</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 262</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 263</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 264</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 265</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 266</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 267</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 268</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 269</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 270</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 271</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 272</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 273</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 274</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 275</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 297</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 298</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 299</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 300</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 301</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 302</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 303</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 304</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 305</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 306</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 307</p>
 [code: mac-names]



* 🔥 **FAIL** <p>Please remove name ID 308</p>
 [code: mac-names]



</div>
</details>

<details>
    <summary>🔥 <b>FAIL</b> Ensure smart dropout control is enabled in "prep" table instructions. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#smart-dropout">smart_dropout</a></summary>
    <div>







* 🔥 **FAIL** <p>The 'prep' table does not contain TrueType instructions enabling smart dropout control. To fix, export the font with autohinting enabled, or run ttfautohint on the font, or run the <code>gftools fix-nonhinting</code> script.</p>
 [code: lacks-smart-dropout]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Check mark characters are in GDEF mark glyph class. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/opentype.html#opentype-gdef-mark-chars">opentype/gdef_mark_chars</a></summary>
    <div>







* ⚠️ **WARN** <p>The following mark characters could be in the GDEF mark glyph class:
uni0488 (U+0488), uni0489 (U+0489), uni20DD (U+20DD) and uni20DE (U+20DE)</p>
 [code: mark-chars]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Check glyphs in mark glyph class are non-spacing. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/opentype.html#opentype-gdef-spacing-marks">opentype/gdef_spacing_marks</a></summary>
    <div>







* ⚠️ **WARN** <p>The following glyphs seem to be spacing (because they have width &gt; 0 on the hmtx table) so they may be in the GDEF mark glyph class by mistake, or they should have zero width instead:
dotbelow (U+0323)</p>
 [code: spacing-mark-glyphs]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Detect any interpolation issues in the font. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#interpolation-issues">interpolation_issues</a></summary>
    <div>







* ⚠️ **WARN** <p>Interpolation issues were found in the font:</p>
<pre><code>- Contour 1 point 6 in glyph 'uni0240' has a kink between location opsz=32,wght=100 and location opsz=32,wght=900
</code></pre>
 [code: interpolation-issues]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Check there are no overlapping path segments <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#overlapping-path-segments">overlapping_path_segments</a></summary>
    <div>







* ⚠️ **WARN** <p>The following glyphs have overlapping path segments:</p>
<pre><code>* uni0195 (U+0195): L&lt;&lt;883.0,558.0&gt;--&lt;1065.0,558.0&gt;&gt; has the same coordinates as a previous segment.

* uni0271 (U+0271): L&lt;&lt;1543.0,0.0&gt;--&lt;1363.0,0.0&gt;&gt; has the same coordinates as a previous segment.

* nlfthook (U+0272): L&lt;&lt;245.0,0.0&gt;--&lt;65.0,0.0&gt;&gt; has the same coordinates as a previous segment.

* epsilon1revclosed (U+025E): L&lt;&lt;286.0,575.0&gt;--&lt;107.0,575.0&gt;&gt; has the same coordinates as a previous segment.

* uni04C8 (U+04C8): L&lt;&lt;955.0,0.0&gt;--&lt;775.0,0.0&gt;&gt; has the same coordinates as a previous segment.

* uni203D (U+203D): L&lt;&lt;519.0,418.0&gt;--&lt;391.0,418.0&gt;&gt; has the same coordinates as a previous segment.

* uni2E18 (U+2E18): L&lt;&lt;519.0,700.0&gt;--&lt;647.0,700.0&gt;&gt; has the same coordinates as a previous segment.

* babygamma (U+0264): L&lt;&lt;672.0,150.0&gt;--&lt;644.0,-20.0&gt;&gt; has the same coordinates as a previous segment.

* omegaclosed (U+0277): L&lt;&lt;904.0,966.0&gt;--&lt;933.0,1132.0&gt;&gt; has the same coordinates as a previous segment.

* vscript (U+028B): L&lt;&lt;473.0,-20.0&gt;--&lt;498.0,152.0&gt;&gt; has the same coordinates as a previous segment.

* archdblsubcomb (U+EEAA): L&lt;&lt;-748.0,-114.0&gt;--&lt;-650.0,-114.0&gt;&gt; has the same coordinates as a previous segment.

* seagullsubcomb (U+EEC5): L&lt;&lt;-651.0,-373.0&gt;--&lt;-755.0,-373.0&gt;&gt; has the same coordinates as a previous segment.
</code></pre>
 [code: overlapping-path-segments]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Check font contains no unreachable glyphs <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#unreachable-glyphs">unreachable_glyphs</a></summary>
    <div>







* ⚠️ **WARN** <p>The following glyphs could not be reached by codepoint or substitution rules:</p>
<pre><code>- _part.t_base

- _part.tcurl_base

- koronisaccentleft.cn

- macrondieresiscomb.cn

- tildemacroncomb.cn

- uni1DC4.cn

- uni1DC6.cn
</code></pre>
 [code: unreachable-glyphs]



</div>
</details>
</div>
</details>

<details><summary>[1] Family checks</summary>
<div>
<details>
    <summary>🔥 <b>FAIL</b> Ensure VFs have 'ital' STAT axis. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/opentype.html#opentype-STAT-ital-axis">opentype/STAT/ital_axis</a></summary>
    <div>







* 🔥 **FAIL** <p>Italic font sources/InterVariable-Italic.ttf has no matching Roman font.</p>
 [code: missing-roman]



</div>
</details>
</div>
</details>




### Summary

| 💥 ERROR | ☠ FATAL | 🔥 FAIL | ⚠️ WARN | ⏩ SKIP | ℹ️ INFO | ✅ PASS | 🔎 DEBUG | 
| ---|---|---|---|---|---|---|---|
| 0 | 0 | 7 | 5 | 17 | 3 | 95 | 0 | 
| 0% | 0% | 6% | 4% | 13% | 2% | 75% | 0% | 



**Note:** The following loglevels were omitted in this report:


* SKIP
* INFO
* PASS
* DEBUG
