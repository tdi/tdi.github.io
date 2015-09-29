Title: Delete until signature in vim
Date: 2015-09-29 16:13
Tags: vim, mutt
Category: tools
Slug: delete-until-signature-in-vim

It has been bugging me for a while. When responding to an email, you often want to delete all the
content (or part of the previous content) until the end of the email's body. However it would be
nice to leave your signature in place. For that I came up with this nifty little vim trick:


    ::vim
    nnoremap <silent> <leader>gr <Esc>d/--\_.*Dariusz<CR>:nohl<CR>O

Assuming that your signature starts with `--` and the following line starts with your name (in my
case it is Dariusz), this will delete all the content from the current line until the signature.
Then it will remove search highlighting, and finally move one line up.

