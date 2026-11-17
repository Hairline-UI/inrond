## FontBakery report

fontbakery version: 1.1.0







## Check results



<details><summary>[6] Intern[opsz,wght].ttf</summary>
<div>
<details>
    <summary>🔥 <b>FAIL</b> Checking OS/2 usWinAscent & usWinDescent. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#family-win-ascent-and-descent">family/win_ascent_and_descent</a></summary>
    <div>







* 🔥 **FAIL** <p>OS/2.usWinAscent value should be equal or greater than 2276, but got 1984 instead</p>
 [code: ascent]



* 🔥 **FAIL** <p>OS/2.usWinDescent value should be equal or greater than 632, but got 494 instead</p>
 [code: descent]



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
    <summary>⚠️ <b>WARN</b> Check glyphs in mark glyph class are non-spacing. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/opentype.html#opentype-gdef-spacing-marks">opentype/gdef_spacing_marks</a></summary>
    <div>







* ⚠️ **WARN** <p>The following glyphs seem to be spacing (because they have width &gt; 0 on the hmtx table) so they may be in the GDEF mark glyph class by mistake, or they should have zero width instead:
dotbelow (U+0323)</p>
 [code: spacing-mark-glyphs]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Check if OS/2 xAvgCharWidth is correct. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/opentype.html#opentype-xavgcharwidth">opentype/xavgcharwidth</a></summary>
    <div>







* ⚠️ **WARN** <p>OS/2 xAvgCharWidth is 1311 but it should be 1187 which corresponds to the average of the widths of all glyphs in the font.</p>
 [code: xAvgCharWidth-wrong]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Detect any interpolation issues in the font. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#interpolation-issues">interpolation_issues</a></summary>
    <div>







* ⚠️ **WARN** <p>Interpolation issues were found in the font:</p>
<pre><code>- Contour 0 point 8 in glyph 'nine.sups' has a kink between location opsz=14,wght=100 and location opsz=14,wght=900

- Contour 0 point 8 in glyph 'nine.sups' has a kink between location opsz=14,wght=900 and location opsz=32,wght=100

- Contour 0 point 8 in glyph 'nine.sups' has a kink between location opsz=32,wght=100 and location opsz=32,wght=900

- Contour 0 point 8 in glyph 'six' has a kink between location opsz=14,wght=100 and location opsz=14,wght=900

- Contour 0 point 0 in glyph 'six' has a kink between location opsz=14,wght=900 and location opsz=32,wght=100

- Contour 0 point 8 in glyph 'six' has a kink between location opsz=14,wght=900 and location opsz=32,wght=100

- Contour 0 point 0 in glyph 'six' has a kink between location opsz=32,wght=100 and location opsz=32,wght=900

- Contour 0 point 8 in glyph 'six' has a kink between location opsz=32,wght=100 and location opsz=32,wght=900

- Contour 0 point 23 in glyph 'two.sups' has a kink between location opsz=14,wght=100 and location opsz=14,wght=900

- Contour 0 point 23 in glyph 'two.sups' has a kink between location opsz=14,wght=900 and location opsz=32,wght=100

- 232 more.
</code></pre>
<p>Use -F or --full-lists to disable shortening of long lists.</p>
 [code: interpolation-issues]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Check there are no overlapping path segments <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#overlapping-path-segments">overlapping_path_segments</a></summary>
    <div>







* ⚠️ **WARN** <p>The following glyphs have overlapping path segments:</p>
<pre><code>* uni20BA (U+20BA): B&lt;&lt;313.0,-11.0&gt;-&lt;313.0,-11.0&gt;-&lt;313.0,-11.0&gt;&gt; has the same coordinates as a previous segment.

* uni20BA (U+20BA): B&lt;&lt;313.0,-11.0&gt;-&lt;313.0,-11.0&gt;-&lt;313.0,-11.0&gt;&gt; has the same coordinates as a previous segment.
</code></pre>
 [code: overlapping-path-segments]



</div>
</details>
</div>
</details>




### Summary

| 💥 ERROR | ☠ FATAL | 🔥 FAIL | ⚠️ WARN | ⏩ SKIP | ℹ️ INFO | ✅ PASS | 🔎 DEBUG | 
| ---|---|---|---|---|---|---|---|
| 0 | 0 | 2 | 4 | 19 | 3 | 99 | 0 | 
| 0% | 0% | 2% | 3% | 15% | 2% | 78% | 0% | 



**Note:** The following loglevels were omitted in this report:


* SKIP
* INFO
* PASS
* DEBUG
