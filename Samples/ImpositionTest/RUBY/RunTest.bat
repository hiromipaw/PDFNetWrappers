@echo off
setlocal
set TEST_NAME=ImpositionTest
SET PATH=..\..\..\PDFNetC\Lib;%PATH%
ruby.exe %TEST_NAME%.rb
endlocal
