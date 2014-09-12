Toggle cursorline and cursorcolumn function in VIM
##################################################
:slug: toggle-cursorline-in-vim
:date: 2013/01/30 10:59:09
:tags: vim, viml
:category: tools


It is often very comfortable to see where your cursor in VIM is. To achieve that you can use
cursorcolumn and cursorline to highlight the row and the column in which you are currently present
with your cursor. Below is a function that can be placed in your ``.vimrc`` to toggle such a
behaviour. It is then mapped to ``<leader>cl``, which effectively means that you need to punch ``\cl`` to
make it work. 

.. code-block:: vim

  set cursorline
  set cursorcolumn
  
  fu! ToggleCurline ()
    if &cursorline && &cursorcolumn 
      set nocursorline
      set nocursorcolumn
    else
      set cursorline
      set cursorcolumn
    endif
  endfunction

  map <silent><leader>cl :call ToggleCurline()<CR>


