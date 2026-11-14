## FontBakery report

fontbakery version: 1.1.0







## Check results



<details><summary>[10] InrondSoft-Italic[opsz,wght].ttf</summary>
<div>
<details>
    <summary>🔥 <b>FAIL</b> Check base characters have non-zero advance width. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#base-has-width">base_has_width</a></summary>
    <div>


> 
> Base characters should have non-zero advance width.
> 




> Original proposal: https://github.com/fonttools/fontbakery/issues/4906





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


> 
> Ensure that no glyph lacks its corresponding upper or lower counterpart
> (but only when unicode supports case-mapping).
> 




> Original proposal: https://github.com/googlefonts/fontbakery/issues/3230





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


> 
> A font's winAscent and winDescent values should be greater than or equal to
> the head table's yMax, abs(yMin) values. If they are less than these values,
> clipping can occur on Windows platforms
> (https://github.com/RedHatBrand/Overpass/issues/33).
> 
> If the font includes tall/deep writing systems such as Arabic or Devanagari,
> the winAscent and winDescent can be greater than the yMax and absolute yMin
> values to accommodate vowel marks.
> 
> When the 'win' Metrics are significantly greater than the UPM, the linespacing
> can appear too loose. To counteract this, enabling the OS/2 fsSelection
> bit 7 (Use_Typo_Metrics), will force Windows to use the OS/2 'typo' values
> instead. This means the font developer can control the linespacing with
> the 'typo' values, whilst avoiding clipping by setting the 'win' values to
> values greater than the yMax and absolute yMin.
> 




> Original proposal: https://github.com/fonttools/fontbakery/issues/4829





* 🔥 **FAIL** <p>OS/2.usWinAscent value should be equal or greater than 2269, but got 1984 instead</p>
 [code: ascent]



* 🔥 **FAIL** <p>OS/2.usWinDescent value should be equal or greater than 660, but got 494 instead</p>
 [code: descent]



</div>
</details>

<details>
    <summary>🔥 <b>FAIL</b> Combined length of family and style must not exceed 31 characters. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#name-family-and-style-max-length">name/family_and_style_max_length</a></summary>
    <div>


> 
> This check ensures that the length of name table entries is not
> too long, as this causes problems in some environments.
> 
> Background on length limit (credit to Aaron Bell at google/fonts/issues/9185):
> 
> The font dropdown in Microsoft Office on PC is driven by the older
> GDI font enumeration and rendering technology. GDI uses LOGFONTA
> (https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-logfonta)
> to define the attributes of a font, and CHAR lfFaceName[LF_FACESIZE];
> to define the font name. The problem, though, is that the string lfFaceName
> is restricted to 32 characters, including the terminating NULL.
> 
> In a variable font where the master location is at a location with a
> significant number of characters, say, “ExtraLight”, name ID 1 can become
> quite long (eg: “Chiron Hei HK ExtraLight”). However, in determining the
> font name, Microsoft will prioritize name ID 16 over name ID 1. So this
> lets one reduce the character count back to the standard font name
> (eg: “Chiron Hei HK”).
> 




> Original proposal: https://github.com/fonttools/fontbakery/issues/1488
> See also: https://github.com/fonttools/fontbakery/issues/2179





* 🔥 **FAIL** <p>Name ID 1 'Inrond Soft VF' plus STAT table style combination 'Display ExtraLight' exceeds 31 characters (the combination is 33 characters).</p>
<p>This has been found to cause a fallback font to appear for some accented letters, as well as in some scripts such as Thai, in Microsoft Word on Windows 10 and 11. It can also lead to names which are truncated in the Microsoft Word font menu.</p>
 [code: familyname-plus-stat-entries-too-long]



* 🔥 **FAIL** <p>Name ID 1 'Inrond Soft VF' plus STAT table style combination 'Display ExtraBold' exceeds 31 characters (the combination is 32 characters).</p>
<p>This has been found to cause a fallback font to appear for some accented letters, as well as in some scripts such as Thai, in Microsoft Word on Windows 10 and 11. It can also lead to names which are truncated in the Microsoft Word font menu.</p>
 [code: familyname-plus-stat-entries-too-long]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Check mark characters are in GDEF mark glyph class. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/opentype.html#opentype-gdef-mark-chars">opentype/gdef_mark_chars</a></summary>
    <div>


> 
> Mark characters should be in the GDEF mark glyph class.
> 




> Original proposal: https://github.com/fonttools/fontbakery/issues/2877





* ⚠️ **WARN** <p>The following mark characters could be in the GDEF mark glyph class:
uni0488 (U+0488), uni0489 (U+0489), uni20DD (U+20DD) and uni20DE (U+20DE)</p>
 [code: mark-chars]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Check glyphs in mark glyph class are non-spacing. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/opentype.html#opentype-gdef-spacing-marks">opentype/gdef_spacing_marks</a></summary>
    <div>


> 
> Glyphs in the GDEF mark glyph class should be non-spacing.
> 
> Spacing glyphs in the GDEF mark glyph class may have incorrect anchor
> positioning that was only intended for building composite glyphs during design.
> 




> Original proposal: https://github.com/fonttools/fontbakery/issues/2877





* ⚠️ **WARN** <p>The following glyphs seem to be spacing (because they have width &gt; 0 on the hmtx table) so they may be in the GDEF mark glyph class by mistake, or they should have zero width instead:
dotbelow (U+0323)</p>
 [code: spacing-mark-glyphs]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Ensure files are not too large. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#file-size">file_size</a></summary>
    <div>


> 
> Serving extremely large font files causes usability issues.
> This check ensures that file sizes are reasonable.
> 




> Original proposal: https://github.com/fonttools/fontbakery/issues/3320





* ⚠️ **WARN** <p>Font file is 1.4Mb; ideally it should be less than 1.0Mb</p>
 [code: large-font]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Detect any interpolation issues in the font. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#interpolation-issues">interpolation_issues</a></summary>
    <div>


> 
> When creating a variable font, the designer must make sure that corresponding
> paths have the same start points across masters, as well as that corresponding
> component shapes are placed in the same order within a glyph across masters.
> If this is not done, the glyph will not interpolate correctly.
> 
> Here we check for the presence of potential interpolation errors using the
> fontTools.varLib.interpolatable module.
> 




> Original proposal: https://github.com/fonttools/fontbakery/issues/3930





* ⚠️ **WARN** <p>Interpolation issues were found in the font:</p>
<pre><code>- Contour 0 point 20 in glyph 'uni0286' has a kink between location opsz=14,wght=900 and location opsz=32,wght=100
</code></pre>
 [code: interpolation-issues]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Check there are no overlapping path segments <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#overlapping-path-segments">overlapping_path_segments</a></summary>
    <div>


> 
> Some rasterizers encounter difficulties when rendering glyphs with
> overlapping path segments.
> 
> A path segment is a section of a path defined by two on-curve points.
> When two segments share the same coordinates, they are considered
> overlapping.
> 




> Original proposal: https://github.com/google/fonts/issues/7594#issuecomment-2401909084





* ⚠️ **WARN** <p>The following glyphs have overlapping path segments:</p>
<pre><code>* uni0195 (U+0195): L&lt;&lt;883.0,558.0&gt;--&lt;1065.0,558.0&gt;&gt; has the same coordinates as a previous segment.

* uni0271 (U+0271): L&lt;&lt;1543.0,0.0&gt;--&lt;1363.0,0.0&gt;&gt; has the same coordinates as a previous segment.

* nlfthook (U+0272): L&lt;&lt;245.0,0.0&gt;--&lt;65.0,0.0&gt;&gt; has the same coordinates as a previous segment.

* epsilon1revclosed (U+025E): L&lt;&lt;286.0,575.0&gt;--&lt;107.0,575.0&gt;&gt; has the same coordinates as a previous segment.

* uni04C8 (U+04C8): L&lt;&lt;955.0,0.0&gt;--&lt;775.0,0.0&gt;&gt; has the same coordinates as a previous segment.

* babygamma (U+0264): L&lt;&lt;672.0,150.0&gt;--&lt;644.0,-20.0&gt;&gt; has the same coordinates as a previous segment.

* omegaclosed (U+0277): L&lt;&lt;904.0,966.0&gt;--&lt;933.0,1132.0&gt;&gt; has the same coordinates as a previous segment.

* vscript (U+028B): L&lt;&lt;473.0,-20.0&gt;--&lt;498.0,152.0&gt;&gt; has the same coordinates as a previous segment.

* uni1DE3 (U+1DE3): B&lt;&lt;-262.0,1204.0&gt;-&lt;-262.0,1204.0&gt;-&lt;-262.0,1204.0&gt;&gt; has the same coordinates as a previous segment.
</code></pre>
 [code: overlapping-path-segments]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Check font contains no unreachable glyphs <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#unreachable-glyphs">unreachable_glyphs</a></summary>
    <div>


> 
> Glyphs are either accessible directly through Unicode codepoints or through
> substitution rules.
> 
> In Color Fonts, glyphs are also referenced by the COLR table. And mathematical
> fonts also reference glyphs via the MATH table.
> 
> Any glyphs not accessible by these means are redundant and serve only
> to increase the font's file size.
> 




> Original proposal: https://github.com/fonttools/fontbakery/issues/3160





* ⚠️ **WARN** <p>The following glyphs could not be reached by codepoint or substitution rules:</p>
<pre><code>- _part.cyrtail

- _part.cyrtic

- _part.cyrtic_hook

- _part.cyrtic_left

- _part.t_base

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


> 
> Check that related Upright and Italic VFs have an
> 'ital' axis in the STAT table.
> 
> Since the STAT table can be used to create new instances, it is
> important to ensure that such an 'ital' axis be the last one
> declared in the STAT table so that the eventual naming of new
> instances follows the subfamily traditional scheme (RIBBI / WWS)
> where "Italic" is always last.
> 
> The 'ital' axis should also be strictly boolean, only accepting
> values of 0 (for Uprights) or 1 (for Italics). This usually works
> as a mechanism for selecting between two linked variable font files.
> 
> Also, the axis value name for uprights must be set as elidable.
> 




> Original proposal: https://github.com/fonttools/fontbakery/issues/2934
> See also: https://github.com/fonttools/fontbakery/issues/3668
> See also: https://github.com/fonttools/fontbakery/issues/3669





* 🔥 **FAIL** <p>Italic font fonts/variable/InrondSoft-Italic[opsz,wght].ttf has no matching Roman font.</p>
 [code: missing-roman]



</div>
</details>
</div>
</details>




### Summary

| 💥 ERROR | ☠ FATAL | 🔥 FAIL | ⚠️ WARN | ⏩ SKIP | ℹ️ INFO | ✅ PASS | 🔎 DEBUG | 
| ---|---|---|---|---|---|---|---|
| 0 | 0 | 5 | 6 | 17 | 3 | 96 | 0 | 
| 0% | 0% | 4% | 5% | 13% | 2% | 76% | 0% | 



**Note:** The following loglevels were omitted in this report:


* SKIP
* INFO
* PASS
* DEBUG
