## FontBakery report

fontbakery version: 1.1.0







## Check results



<details><summary>[9] Inrond[ROND,opsz,wght].ttf</summary>
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





* ⚠️ **WARN** <p>Font file is 2.3Mb; ideally it should be less than 1.0Mb</p>
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
<pre><code>- Contour 1 point 14 in glyph 'lambdabar' has a kink between location opsz=32,wght=400,ROND=0 and location opsz=14,wght=100,ROND=0

- Contour 1 point 50 in glyph 'lambdabar' has a kink between location opsz=32,wght=400,ROND=0 and location opsz=14,wght=100,ROND=0

- Contour 1 in glyph '.notdef': becomes underweight between opsz=14,wght=400,ROND=100 and opsz=32,wght=400,ROND=0.

- Contour 1 in glyph '.notdef': becomes underweight between opsz=14,wght=900,ROND=100 and opsz=32,wght=100,ROND=0.

- Contour 0 point 14 in glyph 'lambda' has a kink between location opsz=32,wght=400,ROND=0 and location opsz=14,wght=100,ROND=0

- Contour 0 point 50 in glyph 'lambda' has a kink between location opsz=32,wght=400,ROND=0 and location opsz=14,wght=100,ROND=0
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
<pre><code>* .notdef: B&lt;&lt;1016.0,-416.0&gt;-&lt;1016.0,-416.0&gt;-&lt;1016.0,-416.0&gt;&gt; has the same coordinates as a previous segment.

* .notdef: B&lt;&lt;328.0,-416.0&gt;-&lt;328.0,-416.0&gt;-&lt;328.0,-416.0&gt;&gt; has the same coordinates as a previous segment.

* .notdef: B&lt;&lt;328.0,1856.0&gt;-&lt;328.0,1856.0&gt;-&lt;328.0,1856.0&gt;&gt; has the same coordinates as a previous segment.

* .notdef: B&lt;&lt;1016.0,1856.0&gt;-&lt;1016.0,1856.0&gt;-&lt;1016.0,1856.0&gt;&gt; has the same coordinates as a previous segment.

* .notdef: B&lt;&lt;617.0,-192.0&gt;-&lt;617.0,-192.0&gt;-&lt;617.0,-192.0&gt;&gt; has the same coordinates as a previous segment.

* .notdef: B&lt;&lt;728.0,-64.0&gt;-&lt;728.0,-64.0&gt;-&lt;728.0,-64.0&gt;&gt; has the same coordinates as a previous segment.

* .notdef: B&lt;&lt;768.0,128.0&gt;-&lt;768.0,128.0&gt;-&lt;768.0,128.0&gt;&gt; has the same coordinates as a previous segment.

* .notdef: B&lt;&lt;576.0,128.0&gt;-&lt;576.0,128.0&gt;-&lt;576.0,128.0&gt;&gt; has the same coordinates as a previous segment.

* .notdef: B&lt;&lt;576.0,256.0&gt;-&lt;576.0,256.0&gt;-&lt;576.0,256.0&gt;&gt; has the same coordinates as a previous segment.

* .notdef: B&lt;&lt;768.0,256.0&gt;-&lt;768.0,256.0&gt;-&lt;768.0,256.0&gt;&gt; has the same coordinates as a previous segment.

* 22768 more.
</code></pre>
<p>Use -F or --full-lists to disable shortening of long lists.</p>
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




### Summary

| 💥 ERROR | ☠ FATAL | 🔥 FAIL | ⚠️ WARN | ⏩ SKIP | ℹ️ INFO | ✅ PASS | 🔎 DEBUG | 
| ---|---|---|---|---|---|---|---|
| 0 | 0 | 3 | 6 | 17 | 3 | 98 | 0 | 
| 0% | 0% | 2% | 5% | 13% | 2% | 77% | 0% | 



**Note:** The following loglevels were omitted in this report:


* SKIP
* INFO
* PASS
* DEBUG
