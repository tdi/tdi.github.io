Highlight lines over 79
#######################

:slug: highlight-lines-over-79
:date: 2013/02/02 11:09:54
:tags: vim, python
:category: tools

If you want to stick to PEP8 speccification of Python syntax, you should stick to 79 line length. 
It is very easy to forget to follow that rule, fortunatelly vim can help you. There are many nice
solution to inform you when you go past 79 column. The most generic one is highlighting only the
80th column by setting ``set cursorcolumn`` (or just ``set cc``). This will produce a vertical line
on the column according to your ``textwidth`` variable. You can check this by doing ``:set tw?``.  
If you want some better looking solution try the one I found on stackoverflow. You can adjust the color and linewidth to your
preferences. 

.. code-block:: vim

   highlight OverLength ctermbg=red ctermfg=white guibg=#592929
   match OverLength /\%80v.\+/

