## FontBakery report

fontbakery version: 1.1.0







## Check results



<details><summary>[7] Goeist[wght].ttf</summary>
<div>
<details>
    <summary>⚠️ <b>WARN</b> Check accent of Lcaron, dcaron, lcaron, tcaron <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#alt-caron">alt_caron</a></summary>
    <div>









* ⚠️ **WARN** <p>tcaron is decomposed and therefore could not be checked. Please check manually.</p>
 [code: decomposed-outline]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Detect any interpolation issues in the font. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#interpolation-issues">interpolation_issues</a></summary>
    <div>







* ⚠️ **WARN** <p>Interpolation issues were found in the font:</p>
<pre><code>- Contour 0 point 10 in glyph 'section' has a kink between location wght=100 and location wght=801

- Contour 0 point 68 in glyph 'section' has a kink between location wght=100 and location wght=801

- Contour 2 point 26 in glyph 'copyright' has a kink between location wght=100 and location wght=801

- Contour 1 point 23 in glyph 'uni03060303' has a kink between location wght=100 and location wght=801

- Contour 1 point 31 in glyph 'uni03060303' has a kink between location wght=100 and location wght=801

- Contour 1 point 23 in glyph 'uni03060300' has a kink between location wght=100 and location wght=801

- Contour 1 point 31 in glyph 'uni03060300' has a kink between location wght=100 and location wght=801

- Contour 0 point 0 in glyph 'questiondown.ss08' has a kink between location wght=100 and location wght=801

- Contour 1 point 10 in glyph 'uni01E5' has a kink between location wght=100 and location wght=801

- Contour 0 point 27 in glyph 'uni2089' has a kink between location wght=400 and location wght=100

- 64 more.
</code></pre>
<p>Use -F or --full-lists to disable shortening of long lists.</p>
 [code: interpolation-issues]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Are there caret positions declared for every ligature? <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#ligature-carets">ligature_carets</a></summary>
    <div>







* ⚠️ **WARN** <p>This font lacks caret positioning values for these ligature glyphs:
- hyphen_greater.liga</p>
<pre><code>- hyphen_hyphen_greater.liga

- hyphen_hyphen_hyphen_greater.liga

- less_hyphen.liga

- less_hyphen_greater.liga

- less_hyphen_hyphen.liga

- less_hyphen_hyphen_hyphen.liga
</code></pre>
 [code: incomplete-caret-pos-data]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Ensure variable fonts include an avar table. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#mandatory-avar-table">mandatory_avar_table</a></summary>
    <div>







* ⚠️ **WARN** <p>This variable font does not have an avar table. Most variable fonts should include an avar table to correctly define axes progression rates.</p>
 [code: missing-avar]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Check math signs have the same width. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#math-signs-width">math_signs_width</a></summary>
    <div>







* ⚠️ **WARN** <p>The most common width is 544 among a set of 4 math glyphs.
The following math glyphs have a different width, though:</p>
<p>Width = 558:
plus</p>
<p>Width = 540:
equal, notequal, divide</p>
<p>Width = 500:
logicalnot</p>
<p>Width = 538:
plusminus</p>
<p>Width = 502:
multiply</p>
<p>Width = 520:
minus</p>
<p>Width = 523:
approxequal</p>
 [code: width-outliers]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Check font contains no unreachable glyphs <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#unreachable-glyphs">unreachable_glyphs</a></summary>
    <div>







* ⚠️ **WARN** <p>The following glyphs could not be reached by codepoint or substitution rules:</p>
<pre><code>- blackCircled
</code></pre>
 [code: unreachable-glyphs]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Glyph names are all valid? <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#valid-glyphnames">valid_glyphnames</a></summary>
    <div>







* ⚠️ **WARN** <p>The following glyph names may be too long for some legacy systems which may expect a maximum 31-characters length limit:
hyphen_hyphen_hyphen_greater.liga and periodcentered.loclCAT.case.ss08</p>
 [code: legacy-long-names]



</div>
</details>
</div>
</details>




### Summary

| 💥 ERROR | ☠ FATAL | 🔥 FAIL | ⚠️ WARN | ⏩ SKIP | ℹ️ INFO | ✅ PASS | 🔎 DEBUG | 
| ---|---|---|---|---|---|---|---|
| 0 | 0 | 0 | 7 | 18 | 3 | 99 | 0 | 
| 0% | 0% | 0% | 6% | 14% | 2% | 78% | 0% | 



**Note:** The following loglevels were omitted in this report:


* SKIP
* INFO
* PASS
* DEBUG
