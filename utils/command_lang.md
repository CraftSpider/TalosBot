## Command signature:
^command add [name] [def_string]  
^command edit [name] [def_string]  
^command remove [name]  
^command list

## Possible Operations:

`[if statement](operation)[elif statement](operation)[else](operation)` - if/else if/else block. Parenthesis may contain any valid def_string  
`{command}` - invoke block. runs a given command, or inserts a variable. Must be a Talos builtin command.
            Will likely eventually fix the inconsistency of running commands and inserting variables.

## Possible variables:

`"text"` or `'text'` - string literal  
`0123456789` - int/float literal  
`author` - message author  
&nbsp;&nbsp;&nbsp; `name` - author name  
&nbsp;&nbsp;&nbsp; `nick` - author nickname
&nbsp;&nbsp;&nbsp; `display_name` - author display name
&nbsp;&nbsp;&nbsp; `discriminator` - author discriminator  
&nbsp;&nbsp;&nbsp; `id` - author id  
`role` - author top role  
&nbsp;&nbsp;&nbsp; `name` - role name  
&nbsp;&nbsp;&nbsp; `colour` - role color  
&nbsp;&nbsp;&nbsp; `id` - role id  
`channel` - message channel  
&nbsp;&nbsp;&nbsp; `name` - channel name  
&nbsp;&nbsp;&nbsp; `id` - channel id  
`category` - message category  
&nbsp;&nbsp;&nbsp; `name` - category name  
&nbsp;&nbsp;&nbsp; `id` - category id  

sub-variables are accessed with :  
variables can be accessed with shorthand.  
variables can be inserted as text into a command using the invoke block  
nickname and category may be None. Display name will be nickname if it exists,
otherwise it will be name.
author -> a, role -> r, channel -> ch, category -> cat  
name -> n, discriminator -> disc, colour -> c, display_name -> d/display

## Boolean Operators:

and - logical and  
or - logical or  
not - logical not  
is - equals  
= - equals  
< - less than  
\> - greater than

## Statements:

Boolean statements may contain any set of variables and boolean operators. For example:  
a:n is "CraftSpider" or a:d is "0003" or ch:id is 100012341  
Parenthesis can be used to set read order
