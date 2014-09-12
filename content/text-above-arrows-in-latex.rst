Text above arrows in LaTeX
##########################

:slug: text-above-arrows-in-latex
:date: 2013/01/30 12:00:39
:tags: latex
:category: latex


Sometimes you need to place text above arrows. Let's say you need to write transitions for a labelled transition system. In fact in LaTeX this is not so obvious, especially if you want to have text above and under the arrow. I know of two easy ways to do it.

.. code-block:: latex
   
   $$ E \xrightarrow{\alpha} F $$

The second method.

.. code-block:: latex

   $$ \mathop{\longrightarrow}^_{\alpha} $$
