Title: forwarding messages with attachments in mutt
Date: 2014-09-12 14:30
Tags: mutt
Category: tools

This is a pain for every mutt user. I do not know why this solution is so hard to find. 
Just add these two lines to your `.muttrc`.
    
    set mime_forward
    set mime_forward_rest=yes

This will forward an email with all the attachments, no scripts needed, no fancy tagging or
reediting. 


