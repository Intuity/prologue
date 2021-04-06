# Copyright 2020, Peter Birch, mailto:peter@lightlogic.co.uk
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from random import randint, choice
from pathlib import Path
from unittest.mock import MagicMock, call, PropertyMock, ANY

import pytest

import prologue
from prologue import Prologue
from prologue.common import PrologueError, Line
from prologue.context import Context
from prologue.directives.base import BlockDirective, LineDirective
from prologue.directives.common import DirectiveWrap
from prologue.registry import RegistryFile

from .common import random_str

def test_prologue_bad_delimiter():
    """ Try to setup Prologue with a bad delimiter """
    # Use an empty delimiter
    with pytest.raises(PrologueError) as excinfo:
        Prologue(delimiter="")
    assert "Delimiter should be at least one character" in str(excinfo.value)
    # Use just whitespace
    with pytest.raises(PrologueError) as excinfo:
        Prologue(delimiter="     ")
    assert "Delimiter should be at least one character" in str(excinfo.value)
    # Use mix of whitespace and characters
    with pytest.raises(PrologueError) as excinfo:
        Prologue(delimiter=" / /")
    assert "Delimiter should not contain whitespace" in str(excinfo.value)
    # Check a sane value works
    assert Prologue(delimiter="//").delimiter == "//"

def test_prologue_bad_new_delimiter():
    """ Try to change the Prologue delimiter to a bad value """
    pro = Prologue(delimiter="#")
    # Read back the delimiter
    assert pro.delimiter == "#"
    # Use an empty delimiter
    with pytest.raises(PrologueError) as excinfo:
        pro.delimiter = ""
    assert "Delimiter should be at least one character" in str(excinfo.value)
    # Use just whitespace
    with pytest.raises(PrologueError) as excinfo:
        pro.delimiter = "     "
    assert "Delimiter should be at least one character" in str(excinfo.value)
    # Use mix of whitespace and characters
    with pytest.raises(PrologueError) as excinfo:
        pro.delimiter = " / /"
    assert "Delimiter should not contain whitespace" in str(excinfo.value)
    # Check a sane value works
    pro.delimiter = "//"
    assert pro.delimiter == "//"

def test_prologue_bad_shared():
    """ Try to setup Prologue with a bad shared value """
    # Check a bad value doesn't work
    with pytest.raises(PrologueError) as excinfo:
        Prologue(shared_delimiter="banana")
    assert "Shared delimiter must be True or False: banana" in str(excinfo.value)
    # Check both sane values work
    for val in (True, False):
        assert Prologue(shared_delimiter=val).shared_delimiter == val

def test_prologue_bad_new_shared():
    """ Try to change Prologue's shared delimiter value """
    pro = Prologue()
    # Check a bad value doesn't work
    with pytest.raises(PrologueError) as excinfo:
        pro.shared_delimiter = "banana"
    assert "Shared delimiter should be True or False" in str(excinfo.value)
    # Check both sane values work
    for val in (True, False):
        pro.shared_delimiter = val
        assert pro.shared_delimiter == val

def test_prologue_add_file(mocker):
    """ Test that add file calls to the registry """
    pro = Prologue()
    mocker.patch.object(pro, "registry", autospec=True)
    pro.add_file("test_file_1234")
    pro.registry.add_file.assert_called_once_with("test_file_1234")

def test_prologue_add_folder(mocker):
    """ Test that add folder calls to the registry """
    pro = Prologue()
    mocker.patch.object(pro, "registry", autospec=True)
    pro.add_folder("test_folder_1234", ".txt", True)
    pro.registry.add_folder.assert_called_once_with(
        "test_folder_1234", search_for=".txt", recursive=True
    )

def test_prologue_messages(mocker):
    """ Test that debug messages are logged using 'print' or callback """
    pro        = Prologue()
    mock_print = mocker.patch("builtins.print")
    for func, cb, mtype in [
        (pro.debug_message,   "callback_debug",   "DEBUG"),
        (pro.info_message,    "callback_info",    "INFO" ),
        (pro.warning_message, "callback_warning", "WARN" ),
        (pro.error_message,   "callback_error",   "ERROR"),
    ]:
        # First test logging via 'print' (default behaviour)
        if mtype == "ERROR":
            with pytest.raises(PrologueError) as excinfo:
                func("Hello 1234!")
            assert "Hello 1234!" in str(excinfo.value)
        else:
            func("Hello 1234!")
            mock_print.assert_called_once_with(f"[PROLOGUE:{mtype}] Hello 1234!")
        # Now test logging via callback
        setattr(pro, cb, MagicMock())
        func("Goodbye 9876?")
        getattr(pro, cb).assert_called_once_with("Goodbye 9876?")
        # Reset mocks
        mock_print.reset_mock()
        getattr(pro, cb).reset_mock()

def test_prologue_register_directive():
    """ Test registration of block and line directives """
    pro = Prologue()
    class LineDirx(LineDirective): pass
    class BlockDirx(BlockDirective): pass
    wrap_line  = DirectiveWrap(LineDirx,  [random_str(5, 10)])
    wrap_block = DirectiveWrap(BlockDirx, [random_str(5, 10)], closing=[random_str(5, 10)])
    # Try registration
    pro.register_directive(wrap_line)
    pro.register_directive(wrap_block)
    # Check registrations
    assert pro.get_directive(wrap_line.opening[0])  == wrap_line
    assert pro.get_directive(wrap_block.opening[0]) == wrap_block
    # Try registration a bad directive
    for obj in (random_str(5, 10), randint(1, 1000), Prologue):
        with pytest.raises(PrologueError) as excinfo:
            pro.register_directive(obj)
        assert "Directive type is not known, is it decorated?" == str(excinfo.value)
    # Try overriding existing directive
    class OtherLineDirx(LineDirective): pass
    class OtherBlockDirx(BlockDirective): pass
    other_line  = DirectiveWrap(OtherLineDirx, wrap_line.opening)
    other_block = DirectiveWrap(OtherBlockDirx, wrap_block.opening, closing=wrap_block.closing)
    with pytest.raises(PrologueError) as excinfo:
        pro.register_directive(other_line)
    assert f"Directive already registered for tag '{wrap_line.opening[0]}'" == str(excinfo.value)
    with pytest.raises(PrologueError) as excinfo:
        pro.register_directive(other_block)
    assert f"Directive already registered for tag '{wrap_block.opening[0]}'" == str(excinfo.value)

def test_prologue_get_directive():
    """ Request registered and unregistered directives """
    pro = Prologue()
    # Register a bunch of directives
    class LineDirx(LineDirective): pass
    class BlockDirx(BlockDirective): pass
    line_opens  = [random_str(3, 10) for _x in range(5)]
    block_opens = [random_str(3, 10, avoid=line_opens) for _x in range(5)]
    block_close = [random_str(3, 10, avoid=(line_opens+block_opens)) for _x in range(5)]
    wrap_line   = DirectiveWrap(LineDirx,  line_opens )
    wrap_block  = DirectiveWrap(BlockDirx, block_opens, closing=block_close)
    pro.register_directive(wrap_line)
    pro.register_directive(wrap_block)
    # Test that correct directive is returned each time
    all_tags = line_opens + block_opens + block_close
    for use_shared in (False, True):
        pro.shared_delimiter = use_shared
        for _x in range(100):
            use_bad = choice((True, False))
            tag     = random_str(3, 10, avoid=all_tags) if use_bad else choice(all_tags)
            # If using a bad directive without shared delimiters, expect an exception
            if use_bad and not use_shared:
                with pytest.raises(PrologueError) as excinfo:
                    pro.get_directive(tag)
                assert f"No directive known for tag '{tag}'" == str(excinfo.value)
            # If using a bad directive with shared delimiters, expect None
            elif use_bad and use_shared:
                assert pro.get_directive(tag) == None
            # Otherwise, expect the correct directive to be returned
            else:
                if tag in line_opens:
                    assert pro.get_directive(tag) == wrap_line
                else:
                    assert pro.get_directive(tag) == wrap_block

def test_prologue_evaluate(mocker):
    """ Test evaluation of a Prologue instance """
    # Patch Context
    mock_ctx_cls  = mocker.patch("prologue.Context", autospec=True)
    mock_ctx_inst = []
    def create_context(*args, **kwargs):
        mock_ctx = MagicMock()
        def fake_sub(line):
            print(f"Called fake_sub with {type(line)} {line}")
            return line.encase("start sub " + str(line) + " end sub")
        mock_ctx.substitute.side_effect = fake_sub
        mock_ctx_inst.append(mock_ctx)
        return mock_ctx
    mock_ctx_cls.side_effect = create_context
    # Create a Prologue instance, and patch 'evaluate_inner'
    pro = Prologue()
    mocker.patch.object(pro, "evaluate_inner", autospec=True)
    # Setup some fake lines to be produced by 'evaluate_inner'
    l_file = random_str(20, 30)
    lines  = [
        Line(random_str(30, 50, spaces=True), l_file, idx+1)
        for idx in range(randint(20, 30))
    ]
    def gen_lines(file, ctx):
        for line in lines: yield line
    pro.evaluate_inner.side_effect = gen_lines
    # Call evaluate
    result = [x for x in pro.evaluate(l_file)]
    # Check that only 'str' objects were yielded
    assert len([x for x in result if not isinstance(x, str)]) == 0
    # Check that every line contains substitutions
    assert result == [f"start sub {str(x)} end sub" for x in lines]
    # Check that the lookup has been populated correctly
    assert pro.lookup == [(x.file, x.number) for x in lines]
    # Check calls to 'evaluate_inner'
    pro.evaluate_inner.assert_has_calls([call(l_file, mock_ctx_inst[0])])
    # Check calls to 'substitute'
    mock_ctx_inst[0].substitute.assert_has_calls([call(x) for x in lines])

def test_prologue_resolve():
    """ Test resolving input line number and file path from output line number """
    pro = Prologue()
    # Before populating lookup, check for error
    with pytest.raises(PrologueError) as excinfo:
        pro.resolve(randint(1, 10000))
    assert "Lookup does not yet exist - have you called 'evaluate'?" == str(excinfo.value)
    # Populate the lookup with random entries
    num_before = randint(0, 5)
    num_after  = randint(0, 5)
    def gen_random_entry():
        fake_file = MagicMock()
        fake_file.contents = [
            Line(random_str(20, 30), fake_file, x+1) for x in range(randint(20, 50))
        ]
        fake_file.snippet.return_value = "this is the snippet"
        fake_num    = randint(1, len(fake_file.contents))
        fake_before = min(num_before, fake_num-1)
        fake_after  = min(num_after,  len(fake_file.contents)-fake_num)
        snippet     = [x.encase(f"{x.number:4d}    {str(x)}") for x in (
                fake_file.contents[fake_num-1-fake_before:fake_num+fake_after]
            )
        ]
        snippet[fake_before] = snippet[fake_before].replace("    ", " >> ")
        return (fake_file, fake_num, [str(x) for x in snippet])
    entries    = [gen_random_entry() for _ in range(randint(100, 200))]
    pro.lookup = [(x[0], x[1]) for x in entries]
    # Try using a non-integer
    for obj in (random_str(5, 10), {}, [], Prologue, MagicMock):
        with pytest.raises(PrologueError) as excinfo:
            pro.resolve(obj)
        assert f"Line number must be an integer - not '{obj}'" == str(excinfo.value)
    # Try out-of-range lines
    for _x in range(100):
        too_low = choice((True, False))
        value   = randint(-100, 0) if too_low else randint(len(entries)+1, 300)
        with pytest.raises(PrologueError) as excinfo:
            pro.resolve(value)
        assert f"Line {value} is out of valid range 1-{len(entries)}" == str(excinfo.value)
    # Test random lines
    for _x in range(100):
        entry    = choice(entries)
        out_line = entries.index(entry) + 1
        # Resolve the input file, line number, and snippet
        r_file, line_no, snippet = pro.resolve(
            out_line, before=num_before, after=num_after
        )
        # Check file, line number, and snippet match those in the fake lookup
        assert entry[0] == r_file
        assert entry[1] == line_no
        assert snippet  == "this is the snippet"
        r_file.snippet.assert_has_calls([call(line_no, num_before, num_after)])
        r_file.snippet.reset_mock()

def test_prologue_evaluate_inner_bad_file(mocker):
    """ Check that an error is raised trying to evaluate a non-existent file """
    pro   = Prologue()
    m_reg = mocker.patch.object(pro, "registry", autospec=True)
    # Try a bunch of random file names
    for _x in range(100):
        m_reg.resolve.side_effect = [None]
        f_name = random_str(5, 10) + "." + random_str(5, 10)
        with pytest.raises(PrologueError) as excinfo:
            [x for x in pro.evaluate_inner(f_name, Context(None))]
        assert f"Failed to find file {f_name}" == str(excinfo.value)
        m_reg.resolve.assert_has_calls([call(f_name)])
        m_reg.reset_mock()

def test_prologue_evaluate_inner_bad_context(mocker):
    """ Check that an error is raised when evaluating with a non-Context object """
    pro   = Prologue()
    m_reg = mocker.patch.object(pro, "registry", autospec=True)
    # Try a bunch of random file names
    for _x in range(100):
        m_reg.resolve.side_effect = [MagicMock()]
        f_name  = random_str(5, 10) + "." + random_str(5, 10)
        bad_ctx = choice((
            True, False, {}, random_str(5, 10), randint(1, 10000), [], MagicMock()
        ))
        with pytest.raises(PrologueError) as excinfo:
            next(pro.evaluate_inner(f_name, bad_ctx))
        assert f"An invalid context was provided: {bad_ctx}" == str(excinfo.value)
        m_reg.resolve.assert_has_calls([call(f_name)])
        m_reg.reset_mock()

def test_prologue_evaluate_inner_break_loop(mocker):
    """ Check that an infinite include loop is detected """
    pro   = Prologue()
    m_reg = mocker.patch.object(pro, "registry", autospec=True)
    mocker.patch.object(RegistryFile, "__init__", lambda x: None)
    m_con = mocker.patch.object(RegistryFile, "contents", new_callable=PropertyMock)
    # Create a context with a bunch of mock files
    ctx = Context(pro)
    for _x in range(randint(10, 30)):
        ctx.stack_push(RegistryFile())
        ctx.stack[-1].path = Path(random_str(5, 10) + "." + random_str(5, 10))
    # Try evaluating files that are already on the stack
    for _x in range(100):
        r_file = choice(ctx.stack)
        m_reg.resolve.side_effect = [r_file]
        with pytest.raises(PrologueError) as excinfo:
            next(pro.evaluate_inner(r_file.filename, ctx))
        assert (
            f"Detected infinite recursion when including file '{r_file.filename}'"
            f" - file stack: {', '.join([x.filename for x in ctx.stack])}"
        ) == str(excinfo.value)
        m_reg.resolve.assert_has_calls([call(r_file.filename)])
        m_reg.reset_mock()
    # Check a new file is pushed to the stack
    new_file      = RegistryFile()
    new_file.path = Path(random_str(5, 10) + "." + random_str(5, 10))
    m_reg.resolve.side_effect = [new_file]
    m_con.return_value        = [random_str(5, 10), random_str(5, 10)]
    next(pro.evaluate_inner(new_file.filename, ctx))
    assert ctx.stack[-1] == new_file

def test_prologue_evaluate_inner_plain(mocker):
    """ Check that a plain sequence of lines is reproduced within alteration """
    pro   = Prologue()
    ctx   = Context(pro)
    m_reg = mocker.patch.object(pro, "registry", autospec=True)
    mocker.patch.object(RegistryFile, "__init__", lambda x: None)
    m_con = mocker.patch.object(RegistryFile, "contents", new_callable=PropertyMock)
    # Create a fake file
    r_file      = RegistryFile()
    r_file.path = Path(random_str(5, 10) + "." + random_str(5, 10))
    m_reg.resolve.side_effect = [r_file]
    # Setup fake file contents
    contents = [random_str(10, 50, spaces=True) for _x in range(randint(50, 100))]
    m_con.return_value = contents
    # Pull all lines out of the evaluate loop
    result = [x for x in pro.evaluate_inner(r_file.filename, ctx)]
    # Checks
    assert result == contents
    m_reg.resolve.assert_has_calls([call(r_file.filename)])
    assert ctx.stack == []

def test_prologue_evaluate_inner_line_span(mocker):
    """ Test use of line spanning using '\' to escape new line """
    pro   = Prologue()
    ctx   = Context(pro)
    m_reg = mocker.patch.object(pro, "registry", autospec=True)
    mocker.patch.object(RegistryFile, "__init__", lambda x: None)
    m_con = mocker.patch.object(RegistryFile, "contents", new_callable=PropertyMock)
    # Create a fake file
    r_file      = RegistryFile()
    r_file.path = Path(random_str(5, 10) + "." + random_str(5, 10))
    m_reg.resolve.side_effect = [r_file]
    # Setup fake file contents
    intro  = [random_str(10, 50, spaces=True) for _x in range(randint(5, 10))]
    span   = [(random_str(10, 50, spaces=True) + "\\") for _x in range(randint(5, 10))]
    span  += [random_str(10, 50, spaces=True)]
    outro  = [random_str(10, 50, spaces=True) for _x in range(randint(5, 10))]
    m_con.return_value = intro + span + outro
    # Pull all lines out of the evaluate loop
    result = [x for x in pro.evaluate_inner(r_file.filename, ctx)]
    # Checks
    assert result == intro + ["".join([x.replace("\\", "") for x in span])] + outro
    m_reg.resolve.assert_has_calls([call(r_file.filename)])
    assert ctx.stack == []

@pytest.mark.parametrize("should_yield", [True, False])
def test_prologue_evaluate_inner_line(mocker, should_yield):
    """ Check that a line directive is detected """
    # Choose a delimiter
    delim = choice(("#", "@", "$", "%", "!"))
    # Create preprocessor, context, etc
    pro   = Prologue(delimiter=delim)
    ctx   = Context(pro)
    m_reg = mocker.patch.object(pro, "registry", autospec=True)
    mocker.patch.object(RegistryFile, "__init__", lambda x: None)
    m_con = mocker.patch.object(RegistryFile, "contents", new_callable=PropertyMock)
    # Create a line directive
    dirx_inst = []
    class LineDirx(LineDirective):
        def __init__(self, parent, src_file=None, src_line=0):
            super().__init__(parent, yields=should_yield, src_file=src_file, src_line=src_line)
            dirx_inst.append(self)
    mocker.patch.object(LineDirx, "invoke",   autospec=True)
    mocker.patch.object(LineDirx, "evaluate", autospec=True)
    dirx_text = "LINE DIRX " + random_str(20, 30, spaces=True) + " END LINE"
    def line_eval(self, context):
        yield Line(dirx_text, None, randint(1, 10000))
    LineDirx.evaluate.side_effect = line_eval
    opening = [random_str(5, 10) for _x in range(randint(1, 5))]
    pro.register_directive(DirectiveWrap(LineDirx, opening))
    # Create a fake file
    r_file      = RegistryFile()
    r_file.path = Path(random_str(5, 10) + "." + random_str(5, 10))
    m_reg.resolve.side_effect = [r_file]
    # Setup fake file contents
    contents   = []
    output     = []
    dirx_calls = []
    for idx in range(randint(50, 100)):
        use_dirx = choice((True, False))
        anchor   = choice((True, False))
        argument = random_str(50, 100, spaces=True)
        use_tag  = choice(opening)
        line_txt = ""
        if use_dirx:
            if not anchor: line_txt += random_str(50, 100, spaces=True) + " "
            line_txt += f"{delim}{use_tag} {argument}"
        else:
            line_txt += random_str(50, 100, spaces=True)
        # Accumulate the data to push into evaluate
        contents.append(line_txt)
        # Accumulate expected outputs
        if not (use_dirx and anchor): output.append(line_txt.split(delim)[0])
        if should_yield:
            if use_dirx and     anchor : output.append(dirx_text)
            if use_dirx and not anchor : output.append(dirx_text)
        # Accumulate calls
        if use_dirx: dirx_calls.append(call(ANY, use_tag.lower(), argument))
    m_con.return_value = [Line(x, r_file, i+1) for i, x in enumerate(contents)]
    # Pull all lines out of the evaluate loop
    result = [x for x in pro.evaluate_inner(r_file.filename, ctx)]
    # Checks
    assert len(result) == len(output)
    assert ctx.stack   == []
    m_reg.resolve.assert_has_calls([call(r_file.filename)])
    for got_out, exp_out in zip(result, output):
        assert str(got_out) == exp_out.rstrip(" ")
    LineDirx.invoke.assert_has_calls(dirx_calls)

@pytest.mark.parametrize("should_yield", [True, False])
def test_prologue_evaluate_inner_block(mocker, should_yield):
    """ Check that a block directive is detected """
    # Choose a delimiter
    delim = choice(("#", "@", "$", "%", "!"))
    # Create preprocessor, context, etc
    pro   = Prologue(delimiter=delim)
    ctx   = Context(pro)
    m_reg = mocker.patch.object(pro, "registry", autospec=True)
    mocker.patch.object(RegistryFile, "__init__", lambda x: None)
    m_con = mocker.patch.object(RegistryFile, "contents", new_callable=PropertyMock)
    # Create a line directive
    class BlockDirx(BlockDirective):
        def __init__(self, parent, src_file=None, src_line=0):
            super().__init__(parent, yields=should_yield, src_file=src_file, src_line=src_line)
    mocker.patch.object(BlockDirx, "open",       autospec=True)
    mocker.patch.object(BlockDirx, "transition", autospec=True)
    mocker.patch.object(BlockDirx, "close",      autospec=True)
    mocker.patch.object(BlockDirx, "evaluate",   autospec=True)
    def do_open(self, tag, arguments): self._BlockDirective__opened = True
    def do_close(self, tag, arguments): self._BlockDirective__closed = True
    BlockDirx.open.side_effect  = do_open
    BlockDirx.close.side_effect = do_close
    dirx_text = []
    for _x in range(randint(5, 10)):
        dirx_text.append(random_str(20, 30, spaces=True))
    def block_eval(self, context):
        for line in dirx_text: yield Line(line, None, randint(1, 10000))
    BlockDirx.evaluate.side_effect = block_eval
    opening = [random_str(5, 10) for _x in range(randint(1, 5))]
    closing = [random_str(5, 10, avoid=opening) for _x in range(1, 5)]
    transit = [random_str(5, 10, avoid=opening+closing) for _x in range(1, 5)]
    pro.register_directive(DirectiveWrap(
        BlockDirx, opening, transition=transit, closing=closing
    ))
    # Create a fake file
    r_file      = RegistryFile()
    r_file.path = Path(random_str(5, 10) + "." + random_str(5, 10))
    m_reg.resolve.side_effect = [r_file]
    # Setup fake file contents
    contents    = []
    output      = []
    open_calls  = []
    tran_calls  = []
    close_calls = []
    for idx in range(randint(50, 100)):
        use_dirx  = choice((True, False))
        open_arg  = random_str(50, 100, spaces=True)
        tran_args = [random_str(50, 100, spaces=True) for _x in range(randint(0, 3))]
        close_arg = random_str(50, 100, spaces=True)
        open_tag  = choice(opening)
        close_tag = choice(closing)
        tran_tag  = choice(transit)
        if use_dirx:
            contents.append(f"{delim}{open_tag} {open_arg}")
        else:
            contents.append(random_str(50, 100, spaces=True))
        # If this is a directive, generate transitions and closing
        if use_dirx:
            # Opening block contents
            for _x in range(randint(5, 10)):
                contents.append(random_str(20, 30, spaces=True))
            # Transitions
            for arg in tran_args:
                contents.append(f"{delim}{tran_tag} {arg}")
                for _x in range(5, 10):
                    contents.append(random_str(20, 30, spaces=True))
            contents.append(f"{delim}{close_tag} {close_arg}")
        # Setup expected output
        if       use_dirx and should_yield: output += dirx_text
        elif not use_dirx                 : output.append(contents[-1])
        # Accumulate calls
        if use_dirx:
            open_calls.append(call(ANY, open_tag.lower(), open_arg))
            for arg in tran_args: tran_calls.append(call(ANY, tran_tag.lower(), arg))
            close_calls.append(call(ANY, close_tag.lower(), close_arg))
    m_con.return_value = [Line(x, r_file, i+1) for i, x in enumerate(contents)]
    # Pull all lines out of the evaluate loop
    result = [x for x in pro.evaluate_inner(r_file.filename, ctx)]
    # Checks
    assert len(result) == len(output)
    assert ctx.stack   == []
    m_reg.resolve.assert_has_calls([call(r_file.filename)])
    for got_out, exp_out in zip(result, output):
        assert str(got_out) == exp_out.rstrip(" ")
    BlockDirx.open.assert_has_calls(open_calls)
    BlockDirx.transition.assert_has_calls(tran_calls)
    BlockDirx.close.assert_has_calls(close_calls)

def test_prologue_evaluate_inner_block_floating(mocker):
    """ Test that floating block directives are flagged """
    # Choose a delimiter
    delim = choice(("#", "@", "$", "%", "!"))
    # Create preprocessor, context, etc
    pro   = Prologue(delimiter=delim)
    ctx   = Context(pro)
    m_reg = mocker.patch.object(pro, "registry", autospec=True)
    mocker.patch.object(RegistryFile, "__init__", lambda x: None)
    m_con = mocker.patch.object(RegistryFile, "contents", new_callable=PropertyMock)
    # Create a line directive
    class BlockDirx(BlockDirective):
        def __init__(self, parent):
            super().__init__(parent, yields=True)
    opening = [random_str(5, 10) for _x in range(randint(1, 5))]
    closing = [random_str(5, 10, avoid=opening) for _x in range(1, 5)]
    transit = [random_str(5, 10, avoid=opening+closing) for _x in range(1, 5)]
    pro.register_directive(DirectiveWrap(
        BlockDirx, opening, transition=transit, closing=closing
    ))
    # Create a fake file
    r_file      = RegistryFile()
    r_file.path = Path(random_str(5, 10) + "." + random_str(5, 10))
    m_reg.resolve.side_effect = [r_file]
    # Setup fake file contents
    contents  = []
    used_open = []
    for idx in range(randint(50, 100)):
        if choice((True, False)):
            used_open.append(choice(opening))
            contents.append(
                random_str(50, 100, spaces=True) +
                f" {delim}{used_open[-1]} {random_str(50, 100, spaces=True)}"
            )
        else:
            contents.append(random_str(50, 100, spaces=True))
    m_con.return_value = [Line(x, r_file, i+1) for i, x in enumerate(contents)]
    # Catch the floating block error
    with pytest.raises(PrologueError) as excinfo:
        [x for x in pro.evaluate_inner(r_file.filename, ctx)]
    assert (
        f"The directive '{used_open[0].lower()}' can only be used with an "
        f"anchored delimiter as it is a block directive"
    ) == str(excinfo.value)

def test_prologue_evaluate_inner_block_confused(mocker):
    """ Check that one block can't be closed by another's tags """
    # Choose a delimiter
    delim = choice(("#", "@", "$", "%", "!"))
    # Create a pair of block directives
    class BlockDirA(BlockDirective):
        def __init__(self, parent, src_file=None, src_line=0):
            super().__init__(parent, yields=True, src_file=src_file, src_line=src_line)
    class BlockDirB(BlockDirective):
        def __init__(self, parent, src_file=None, src_line=0):
            super().__init__(parent, yields=True, src_file=src_file, src_line=src_line)
    all_tags   = []
    opening_a  = [random_str(5, 10, avoid=all_tags) for _x in range(randint(1, 5))]
    all_tags  += opening_a
    closing_a  = [random_str(5, 10, avoid=all_tags) for _x in range(randint(1, 5))]
    all_tags  += closing_a
    transit_a  = [random_str(5, 10, avoid=all_tags) for _x in range(randint(1, 5))]
    all_tags  += transit_a
    opening_b  = [random_str(5, 10, avoid=all_tags) for _x in range(randint(1, 5))]
    all_tags  += opening_b
    closing_b  = [random_str(5, 10, avoid=all_tags) for _x in range(randint(1, 5))]
    all_tags  += closing_b
    transit_b  = [random_str(5, 10, avoid=all_tags) for _x in range(randint(1, 5))]
    # Create a fake file
    mocker.patch.object(RegistryFile, "__init__", lambda x: None)
    r_file      = RegistryFile()
    r_file.path = Path(random_str(5, 10) + "." + random_str(5, 10))
    # Create preprocessor, context, etc
    for _x in range(100):
        pro   = Prologue(delimiter=delim)
        ctx   = Context(pro)
        m_reg = mocker.patch.object(pro, "registry", autospec=True)
        m_reg.resolve.side_effect = [r_file]
        m_con = mocker.patch.object(RegistryFile, "contents", new_callable=PropertyMock)
        pro.register_directive(DirectiveWrap(
            BlockDirA, opening_a, transition=transit_a, closing=closing_a
        ))
        pro.register_directive(DirectiveWrap(
            BlockDirB, opening_b, transition=transit_b, closing=closing_b
        ))
        # Setup fake file contents
        bad_tag   = choice(transit_b + closing_b)
        contents  = []
        contents += [random_str(50, 100, spaces=True) for _x in range(randint(5, 10))]
        contents += [f"{delim}{choice(opening_a)} {random_str(50, 100, spaces=True)}"]
        contents += [random_str(50, 100, spaces=True) for _x in range(randint(5, 10))]
        contents += [f"{delim}{bad_tag} {random_str(50, 100, spaces=True)}"]
        contents += [random_str(50, 100, spaces=True) for _x in range(randint(5, 10))]
        m_con.return_value = [Line(x, r_file, i+1) for i, x in enumerate(contents)]
        # Expect an unexpected transition tag
        with pytest.raises(PrologueError) as excinfo:
            [x for x in pro.evaluate_inner(r_file.filename, ctx)]
        if bad_tag in transit_b:
            assert (
                f"Transition tag '{bad_tag.lower()}' was not expected"
            ) == str(excinfo.value)
        else:
            assert (
                f"Closing tag '{bad_tag.lower()}' was not expected"
            ) == str(excinfo.value)

def test_prologue_evaluate_inner_block_trailing(mocker):
    """ Check that unclosed blocks at the end of the file are detected """
    # Choose a delimiter
    delim = choice(("#", "@", "$", "%", "!"))
    # Create a pair of block directives
    dirx_inst = []
    class BlockDirx(BlockDirective):
        def __init__(self, parent, src_file, src_line):
            super().__init__(parent, yields=True, src_file=src_file, src_line=src_line)
            dirx_inst.append(self)
    opening = [random_str(5, 10) for _x in range(randint(1, 5))]
    closing = [random_str(5, 10, avoid=opening) for _x in range(randint(1, 5))]
    transit = [random_str(5, 10, avoid=opening+closing) for _x in range(randint(1, 5))]
    BlockDirx.OPENING = opening
    # Create a fake file
    mocker.patch.object(RegistryFile, "__init__", lambda x: None)
    r_file      = RegistryFile()
    r_file.path = Path(random_str(5, 10) + "." + random_str(5, 10))
    # Create preprocessor, context, etc
    for _x in range(100):
        pro   = Prologue(delimiter=delim)
        ctx   = Context(pro)
        m_reg = mocker.patch.object(pro, "registry", autospec=True)
        m_reg.resolve.side_effect = [r_file]
        m_con = mocker.patch.object(RegistryFile, "contents", new_callable=PropertyMock)
        pro.register_directive(DirectiveWrap(
            BlockDirx, opening, transition=transit, closing=closing
        ))
        # Setup fake file contents
        contents  = []
        contents += [random_str(50, 100, spaces=True) for _x in range(randint(5, 10))]
        open_idx  = len(contents)
        contents += [f"{delim}{choice(opening)} {random_str(50, 100, spaces=True)}"]
        contents += [random_str(50, 100, spaces=True) for _x in range(randint(5, 10))]
        for _y in range(randint(0, 3)):
            contents += [f"{delim}{choice(transit)} {random_str(50, 100, spaces=True)}"]
            contents += [random_str(50, 100, spaces=True) for _x in range(randint(5, 10))]
        m_con.return_value = [Line(x, r_file, i+1) for i, x in enumerate(contents)]
        # Expected an unclosed directive
        with pytest.raises(PrologueError) as excinfo:
            [x for x in pro.evaluate_inner(r_file.filename, ctx)]
        assert str(excinfo.value).startswith(
            f"Unmatched BlockDirx block directive in {r_file.path}:{open_idx+1}:"
        )

def test_prologue_evaluate_inner_stack_corrupt(mocker):
    """ Check that unclosed blocks at the end of the file are detected """
    # Choose a delimiter
    delim = choice(("#", "@", "$", "%", "!"))
    # Create a pair of block directives
    dirx_inst = []
    class BlockDirx(BlockDirective):
        def __init__(self, parent, src_file=None, src_line=0):
            super().__init__(parent, yields=True, src_file=src_file, src_line=src_line)
            dirx_inst.append(self)
    opening = [random_str(5, 10) for _x in range(randint(1, 5))]
    closing = [random_str(5, 10, avoid=opening) for _x in range(randint(1, 5))]
    transit = [random_str(5, 10, avoid=opening+closing) for _x in range(randint(1, 5))]
    BlockDirx.OPENING = opening
    # Create a fake file
    mocker.patch.object(RegistryFile, "__init__", lambda x: None)
    r_file      = RegistryFile()
    r_file.path = Path(random_str(5, 10) + "." + random_str(5, 10))
    # Create preprocessor, context, etc
    for _x in range(100):
        pro   = Prologue(delimiter=delim)
        ctx   = Context(pro)
        m_reg = mocker.patch.object(pro, "registry", autospec=True)
        m_reg.resolve.side_effect = [r_file]
        m_con = mocker.patch.object(RegistryFile, "contents", new_callable=PropertyMock)
        pro.register_directive(DirectiveWrap(
            BlockDirx, opening, transition=transit, closing=closing
        ))
        # Stub stack_pop to return wrong file
        mocker.patch.object(ctx, "stack_pop", autospec=True)
        ctx.stack_pop.return_value = RegistryFile()
        # Setup fake file contents
        contents  = []
        contents += [random_str(50, 100, spaces=True) for _x in range(randint(5, 10))]
        contents += [f"{delim}{choice(opening)} {random_str(50, 100, spaces=True)}"]
        contents += [random_str(50, 100, spaces=True) for _x in range(randint(5, 10))]
        contents += [f"{delim}{choice(closing)} {random_str(50, 100, spaces=True)}"]
        m_con.return_value = [Line(x, r_file, i+1) for i, x in enumerate(contents)]
        # Expected an unclosed directive
        with pytest.raises(PrologueError) as excinfo:
            [x for x in pro.evaluate_inner(r_file.filename, ctx)]
        assert "File stack has been corrupted" in str(excinfo.value)
