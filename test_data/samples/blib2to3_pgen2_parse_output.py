# Copied from the `black` project.  

# Copyright 2004-2005 Elemental Security, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

# A. HISTORY OF THE SOFTWARE
# ==========================
# 
# Python was created in the early 1990s by Guido van Rossum at Stichting
# Mathematisch Centrum (CWI, see https://www.cwi.nl) in the Netherlands
# as a successor of a language called ABC.  Guido remains Python's
# principal author, although it includes many contributions from others.
# 
# In 1995, Guido continued his work on Python at the Corporation for
# National Research Initiatives (CNRI, see https://www.cnri.reston.va.us)
# in Reston, Virginia where he released several versions of the
# software.
# 
# In May 2000, Guido and the Python core development team moved to
# BeOpen.com to form the BeOpen PythonLabs team.  In October of the same
# year, the PythonLabs team moved to Digital Creations, which became
# Zope Corporation.  In 2001, the Python Software Foundation (PSF, see
# https://www.python.org/psf/) was formed, a non-profit organization
# created specifically to own Python-related Intellectual Property.
# Zope Corporation was a sponsoring member of the PSF.
# 
# All Python releases are Open Source (see https://opensource.org for
# the Open Source Definition).  Historically, most, but not all, Python
# releases have also been GPL-compatible; the table below summarizes
# the various releases.
# 
#     Release         Derived     Year        Owner       GPL-
#                     from                                compatible? (1)
# 
#     0.9.0 thru 1.2              1991-1995   CWI         yes
#     1.3 thru 1.5.2  1.2         1995-1999   CNRI        yes
#     1.6             1.5.2       2000        CNRI        no
#     2.0             1.6         2000        BeOpen.com  no
#     1.6.1           1.6         2001        CNRI        yes (2)
#     2.1             2.0+1.6.1   2001        PSF         no
#     2.0.1           2.0+1.6.1   2001        PSF         yes
#     2.1.1           2.1+2.0.1   2001        PSF         yes
#     2.1.2           2.1.1       2002        PSF         yes
#     2.1.3           2.1.2       2002        PSF         yes
#     2.2 and above   2.1.1       2001-now    PSF         yes
# 
# Footnotes:
# 
# (1) GPL-compatible doesn't mean that we're distributing Python under
#     the GPL.  All Python licenses, unlike the GPL, let you distribute
#     a modified version without making your changes open source.  The
#     GPL-compatible licenses make it possible to combine Python with
#     other software that is released under the GPL; the others don't.
# 
# (2) According to Richard Stallman, 1.6.1 is not GPL-compatible,
#     because its license has a choice of law clause.  According to
#     CNRI, however, Stallman's lawyer has told CNRI's lawyer that 1.6.1
#     is "not incompatible" with the GPL.
# 
# Thanks to the many outside volunteers who have worked under Guido's
# direction to make these releases possible.
# 
# 
# B. TERMS AND CONDITIONS FOR ACCESSING OR OTHERWISE USING PYTHON
# ===============================================================
# 
# PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
# --------------------------------------------
# 
# 1. This LICENSE AGREEMENT is between the Python Software Foundation
# ("PSF"), and the Individual or Organization ("Licensee") accessing and
# otherwise using this software ("Python") in source or binary form and
# its associated documentation.
# 
# 2. Subject to the terms and conditions of this License Agreement, PSF hereby
# grants Licensee a nonexclusive, royalty-free, world-wide license to reproduce,
# analyze, test, perform and/or display publicly, prepare derivative works,
# distribute, and otherwise use Python alone or in any derivative version,
# provided, however, that PSF's License Agreement and PSF's notice of copyright,
# i.e., "Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010,
# 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018 Python Software Foundation; All
# Rights Reserved" are retained in Python alone or in any derivative version
# prepared by Licensee.
# 
# 3. In the event Licensee prepares a derivative work that is based on
# or incorporates Python or any part thereof, and wants to make
# the derivative work available to others as provided herein, then
# Licensee hereby agrees to include in any such work a brief summary of
# the changes made to Python.
# 
# 4. PSF is making Python available to Licensee on an "AS IS"
# basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR
# IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND
# DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS
# FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT
# INFRINGE ANY THIRD PARTY RIGHTS.
# 
# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON
# FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS AS
# A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON,
# OR ANY DERIVATIVE THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.
# 
# 6. This License Agreement will automatically terminate upon a material
# breach of its terms and conditions.
# 
# 7. Nothing in this License Agreement shall be deemed to create any
# relationship of agency, partnership, or joint venture between PSF and
# Licensee.  This License Agreement does not grant permission to use PSF
# trademarks or trade name in a trademark sense to endorse or promote
# products or services of Licensee, or any third party.
# 
# 8. By copying, installing or otherwise using Python, Licensee
# agrees to be bound by the terms and conditions of this License
# Agreement.
# 
# 
# BEOPEN.COM LICENSE AGREEMENT FOR PYTHON 2.0
# -------------------------------------------
# 
# BEOPEN PYTHON OPEN SOURCE LICENSE AGREEMENT VERSION 1
# 
# 1. This LICENSE AGREEMENT is between BeOpen.com ("BeOpen"), having an
# office at 160 Saratoga Avenue, Santa Clara, CA 95051, and the
# Individual or Organization ("Licensee") accessing and otherwise using
# this software in source or binary form and its associated
# documentation ("the Software").
# 
# 2. Subject to the terms and conditions of this BeOpen Python License
# Agreement, BeOpen hereby grants Licensee a non-exclusive,
# royalty-free, world-wide license to reproduce, analyze, test, perform
# and/or display publicly, prepare derivative works, distribute, and
# otherwise use the Software alone or in any derivative version,
# provided, however, that the BeOpen Python License is retained in the
# Software, alone or in any derivative version prepared by Licensee.
# 
# 3. BeOpen is making the Software available to Licensee on an "AS IS"
# basis.  BEOPEN MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR
# IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, BEOPEN MAKES NO AND
# DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS
# FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF THE SOFTWARE WILL NOT
# INFRINGE ANY THIRD PARTY RIGHTS.
# 
# 4. BEOPEN SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF THE
# SOFTWARE FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS
# AS A RESULT OF USING, MODIFYING OR DISTRIBUTING THE SOFTWARE, OR ANY
# DERIVATIVE THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.
# 
# 5. This License Agreement will automatically terminate upon a material
# breach of its terms and conditions.
# 
# 6. This License Agreement shall be governed by and interpreted in all
# respects by the law of the State of California, excluding conflict of
# law provisions.  Nothing in this License Agreement shall be deemed to
# create any relationship of agency, partnership, or joint venture
# between BeOpen and Licensee.  This License Agreement does not grant
# permission to use BeOpen trademarks or trade names in a trademark
# sense to endorse or promote products or services of Licensee, or any
# third party.  As an exception, the "BeOpen Python" logos available at
# http://www.pythonlabs.com/logos.html may be used according to the
# permissions granted on that web page.
# 
# 7. By copying, installing or otherwise using the software, Licensee
# agrees to be bound by the terms and conditions of this License
# Agreement.
# 
# 
# CNRI LICENSE AGREEMENT FOR PYTHON 1.6.1
# ---------------------------------------
# 
# 1. This LICENSE AGREEMENT is between the Corporation for National
# Research Initiatives, having an office at 1895 Preston White Drive,
# Reston, VA 20191 ("CNRI"), and the Individual or Organization
# ("Licensee") accessing and otherwise using Python 1.6.1 software in
# source or binary form and its associated documentation.
# 
# 2. Subject to the terms and conditions of this License Agreement, CNRI
# hereby grants Licensee a nonexclusive, royalty-free, world-wide
# license to reproduce, analyze, test, perform and/or display publicly,
# prepare derivative works, distribute, and otherwise use Python 1.6.1
# alone or in any derivative version, provided, however, that CNRI's
# License Agreement and CNRI's notice of copyright, i.e., "Copyright (c)
# 1995-2001 Corporation for National Research Initiatives; All Rights
# Reserved" are retained in Python 1.6.1 alone or in any derivative
# version prepared by Licensee.  Alternately, in lieu of CNRI's License
# Agreement, Licensee may substitute the following text (omitting the
# quotes): "Python 1.6.1 is made available subject to the terms and
# conditions in CNRI's License Agreement.  This Agreement together with
# Python 1.6.1 may be located on the Internet using the following
# unique, persistent identifier (known as a handle): 1895.22/1013.  This
# Agreement may also be obtained from a proxy server on the Internet
# using the following URL: http://hdl.handle.net/1895.22/1013".
# 
# 3. In the event Licensee prepares a derivative work that is based on
# or incorporates Python 1.6.1 or any part thereof, and wants to make
# the derivative work available to others as provided herein, then
# Licensee hereby agrees to include in any such work a brief summary of
# the changes made to Python 1.6.1.
# 
# 4. CNRI is making Python 1.6.1 available to Licensee on an "AS IS"
# basis.  CNRI MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR
# IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, CNRI MAKES NO AND
# DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS
# FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON 1.6.1 WILL NOT
# INFRINGE ANY THIRD PARTY RIGHTS.
# 
# 5. CNRI SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON
# 1.6.1 FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS AS
# A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON 1.6.1,
# OR ANY DERIVATIVE THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.
# 
# 6. This License Agreement will automatically terminate upon a material
# breach of its terms and conditions.
# 
# 7. This License Agreement shall be governed by the federal
# intellectual property law of the United States, including without
# limitation the federal copyright law, and, to the extent such
# U.S. federal law does not apply, by the law of the Commonwealth of
# Virginia, excluding Virginia's conflict of law provisions.
# Notwithstanding the foregoing, with regard to derivative works based
# on Python 1.6.1 that incorporate non-separable material that was
# previously distributed under the GNU General Public License (GPL), the
# law of the Commonwealth of Virginia shall govern this License
# Agreement only as to issues arising under or with respect to
# Paragraphs 4, 5, and 7 of this License Agreement.  Nothing in this
# License Agreement shall be deemed to create any relationship of
# agency, partnership, or joint venture between CNRI and Licensee.  This
# License Agreement does not grant permission to use CNRI trademarks or
# trade name in a trademark sense to endorse or promote products or
# services of Licensee, or any third party.
# 
# 8. By clicking on the "ACCEPT" button where indicated, or by copying,
# installing or otherwise using Python 1.6.1, Licensee agrees to be
# bound by the terms and conditions of this License Agreement.
# 
#         ACCEPT
# 
# 
# CWI LICENSE AGREEMENT FOR PYTHON 0.9.0 THROUGH 1.2
# --------------------------------------------------
# 
# Copyright (c) 1991 - 1995, Stichting Mathematisch Centrum Amsterdam,
# The Netherlands.  All rights reserved.
# 
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appear in all copies and that
# both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of Stichting Mathematisch
# Centrum or CWI not be used in advertising or publicity pertaining to
# distribution of the software without specific, written prior
# permission.
# 
# STICHTING MATHEMATISCH CENTRUM DISCLAIMS ALL WARRANTIES WITH REGARD TO
# THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS, IN NO EVENT SHALL STICHTING MATHEMATISCH CENTRUM BE LIABLE
# FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


"""Parser engine for the grammar tables generated by pgen.

The grammar table must be loaded first.

See Parser/parser.c in the Python distribution for additional info on
how this parsing engine works.

"""
import copy
from contextlib import contextmanager

# Local imports
from . import grammar, token, tokenize
from typing import (
    cast,
    Any,
    Optional,
    Text,
    Union,
    Tuple,
    Dict,
    List,
    Iterator,
    Callable,
    Set,
    TYPE_CHECKING,
)
from blib2to3.pgen2.grammar import Grammar
from blib2to3.pytree import convert, NL, Context, RawNode, Leaf, Node

if TYPE_CHECKING:
    from blib2to3.driver import TokenProxy


Results = Dict[Text, NL]
Convert = Callable[[Grammar, RawNode], Union[Node, Leaf]]
DFA = List[List[Tuple[int, int]]]
DFAS = Tuple[DFA, Dict[int, int]]


def lam_sub(grammar: Grammar, node: RawNode) -> NL:
    assert node[3] is not None
    return Node(type=node[0], children=node[3], context=node[2])


# A placeholder node, used when parser is backtracking.
DUMMY_NODE = (-1, None, None, None)


def stack_copy(
    stack: List[Tuple[DFAS, int, RawNode]]
) -> List[Tuple[DFAS, int, RawNode]]:
    """Nodeless stack copy."""
    return [(dfa, label, DUMMY_NODE) for dfa, label, _ in stack]


class ParseError(Exception):
    """Exception to signal the parser is stuck."""

    def __init__(
        self, msg: Text, type: Optional[int], value: Optional[Text], context: Context
    ) -> None:
        Exception.__init__(
            self, "%s: type=%r, value=%r, context=%r" % (msg, type, value, context)
        )
        self.msg = msg
        self.type = type
        self.value = value
        self.context = context


class Recorder:
    def __init__(self, parser: "Parser", ilabels: List[int], context: Context) -> None:
        self.parser = parser
        self._ilabels = ilabels
        self.context = context  # not really matter

        self._dead_ilabels: Set[int] = set()
        self._start_point = self.parser.stack
        self._points = {ilabel: stack_copy(self._start_point) for ilabel in ilabels}

    @property
    def ilabels(self) -> Set[int]:
        return self._dead_ilabels.symmetric_difference(self._ilabels)

    @contextmanager
    def switch_to(self, ilabel: int) -> Iterator[None]:
        with self.backtrack():
            self.parser.stack = self._points[ilabel]
            try:
                yield
            except ParseError:
                self._dead_ilabels.add(ilabel)
            finally:
                self.parser.stack = self._start_point

    @contextmanager
    def backtrack(self) -> Iterator[None]:
        """
        Use the node-level invariant ones for basic parsing operations (push/pop/shift).
        These still will operate on the stack; but they won't create any new nodes, or
        modify the contents of any other existing nodes.

        This saves us a ton of time when we are backtracking, since we
        want to restore to the initial state as quick as possible, which
        can only be done by having as little mutatations as possible.
        """
        is_backtracking = self.parser.is_backtracking
        try:
            self.parser.is_backtracking = True
            yield
        finally:
            self.parser.is_backtracking = is_backtracking

    def add_token(self, tok_type: int, tok_val: Text, raw: bool = False) -> None:
        func: Callable[..., Any]
        if raw:
            func = self.parser._addtoken
        else:
            func = self.parser.addtoken

        for ilabel in self.ilabels:
            with self.switch_to(ilabel):
                args = [tok_type, tok_val, self.context]
                if raw:
                    args.insert(0, ilabel)
                func(*args)

    def determine_route(self, value: Text = None, force: bool = False) -> Optional[int]:
        alive_ilabels = self.ilabels
        if len(alive_ilabels) == 0:
            *_, most_successful_ilabel = self._dead_ilabels
            raise ParseError("bad input", most_successful_ilabel, value, self.context)

        ilabel, *rest = alive_ilabels
        if force or not rest:
            return ilabel
        else:
            return None


class Parser(object):
    """Parser engine.

    The proper usage sequence is:

    p = Parser(grammar, [converter])  # create instance
    p.setup([start])                  # prepare for parsing
    <for each input token>:
        if p.addtoken(...):           # parse a token; may raise ParseError
            break
    root = p.rootnode                 # root of abstract syntax tree

    A Parser instance may be reused by calling setup() repeatedly.

    A Parser instance contains state pertaining to the current token
    sequence, and should not be used concurrently by different threads
    to parse separate token sequences.

    See driver.py for how to get input tokens by tokenizing a file or
    string.

    Parsing is complete when addtoken() returns True; the root of the
    abstract syntax tree can then be retrieved from the rootnode
    instance variable.  When a syntax error occurs, addtoken() raises
    the ParseError exception.  There is no error recovery; the parser
    cannot be used after a syntax error was reported (but it can be
    reinitialized by calling setup()).

    """

    def __init__(self, grammar: Grammar, convert: Optional[Convert] = None) -> None:
        """Constructor.

        The grammar argument is a grammar.Grammar instance; see the
        grammar module for more information.

        The parser is not ready yet for parsing; you must call the
        setup() method to get it started.

        The optional convert argument is a function mapping concrete
        syntax tree nodes to abstract syntax tree nodes.  If not
        given, no conversion is done and the syntax tree produced is
        the concrete syntax tree.  If given, it must be a function of
        two arguments, the first being the grammar (a grammar.Grammar
        instance), and the second being the concrete syntax tree node
        to be converted.  The syntax tree is converted from the bottom
        up.

        **post-note: the convert argument is ignored since for Black's
        usage, convert will always be blib2to3.pytree.convert. Allowing
        this to be dynamic hurts mypyc's ability to use early binding.
        These docs are left for historical and informational value.

        A concrete syntax tree node is a (type, value, context, nodes)
        tuple, where type is the node type (a token or symbol number),
        value is None for symbols and a string for tokens, context is
        None or an opaque value used for error reporting (typically a
        (lineno, offset) pair), and nodes is a list of children for
        symbols, and None for tokens.

        An abstract syntax tree node may be anything; this is entirely
        up to the converter function.

        """
        self.grammar = grammar
        # See note in docstring above. TL;DR this is ignored.
        self.convert = convert or lam_sub
        self.is_backtracking = False

    def setup(self, proxy: "TokenProxy", start: Optional[int] = None) -> None:
        """Prepare for parsing.

        This *must* be called before starting to parse.

        The optional argument is an alternative start symbol; it
        defaults to the grammar's start symbol.

        You can use a Parser instance to parse any number of programs;
        each time you call setup() the parser is reset to an initial
        state determined by the (implicit or explicit) start symbol.

        """
        if start is None:
            start = self.grammar.start
        # Each stack entry is a tuple: (dfa, state, node).
        # A node is a tuple: (type, value, context, children),
        # where children is a list of nodes or None, and context may be None.
        newnode: RawNode = (start, None, None, [])
        stackentry = (self.grammar.dfas[start], 0, newnode)
        self.stack: List[Tuple[DFAS, int, RawNode]] = [stackentry]
        self.rootnode: Optional[NL] = None
        self.used_names: Set[str] = set()
        self.proxy = proxy

    def _addtoken(self, ilabel: int, type: int, value: Text, context: Context) -> bool:
        # Loop until the token is shifted; may raise exceptions
        while True:
            dfa, state, node = self.stack[-1]
            states, first = dfa
            arcs = states[state]
            # Look for a state with this label
            for i, newstate in arcs:
                t = self.grammar.labels[i][0]
                if t >= 256:
                    # See if it's a symbol and if we're in its first set
                    itsdfa = self.grammar.dfas[t]
                    itsstates, itsfirst = itsdfa
                    if ilabel in itsfirst:
                        # Push a symbol
                        self.push(t, itsdfa, newstate, context)
                        break  # To continue the outer while loop

                elif ilabel == i:
                    # Look it up in the list of labels
                    # Shift a token; we're done with it
                    self.shift(type, value, newstate, context)
                    # Pop while we are in an accept-only state
                    state = newstate
                    while states[state] == [(0, state)]:
                        self.pop()
                        if not self.stack:
                            # Done parsing!
                            return True
                        dfa, state, node = self.stack[-1]
                        states, first = dfa
                    # Done with this token
                    return False

            else:
                if (0, state) in arcs:
                    # An accepting state, pop it and try something else
                    self.pop()
                    if not self.stack:
                        # Done parsing, but another token is input
                        raise ParseError("too much input", type, value, context)
                else:
                    # No success finding a transition
                    raise ParseError("bad input", type, value, context)

    def addtoken(self, type: int, value: Text, context: Context) -> bool:
        """Add a token; return True iff this is the end of the program."""
        # Map from token to label
        ilabels = self.classify(type, value, context)
        assert len(ilabels) >= 1

        # If we have only one state to advance, we'll directly
        # take it as is.
        if len(ilabels) == 1:
            [ilabel] = ilabels
            return self._addtoken(ilabel, type, value, context)

        # If there are multiple states which we can advance (only
        # happen under soft-keywords), then we will try all of them
        # in parallel and as soon as one state can reach further than
        # the rest, we'll choose that one. This is a pretty hacky
        # and hopefully temporary algorithm.
        #
        # For a more detailed explanation, check out this post:
        # https://tree.science/what-the-backtracking.html

        with self.proxy.release() as proxy:
            counter, force = 0, False
            recorder = Recorder(self, ilabels, context)
            recorder.add_token(type, value, raw=True)

            next_token_value = value
            while recorder.determine_route(next_token_value) is None:
                if not proxy.can_advance(counter):
                    force = True
                    break

                next_token_type, next_token_value, *_ = proxy.eat(counter)
                if next_token_type in (tokenize.COMMENT, tokenize.NL):
                    counter += 1
                    continue

                if next_token_type == tokenize.OP:
                    next_token_type = grammar.opmap[next_token_value]

                recorder.add_token(next_token_type, next_token_value)
                counter += 1

            ilabel = cast(int, recorder.determine_route(next_token_value, force=force))
            assert ilabel is not None

        return self._addtoken(ilabel, type, value, context)

    def classify(self, type: int, value: Text, context: Context) -> List[int]:
        """Turn a token into a label.  (Internal)

        Depending on whether the value is a soft-keyword or not,
        this function may return multiple labels to choose from."""
        if type == token.NAME:
            # Keep a listing of all used names
            self.used_names.add(value)
            # Check for reserved words
            if value in self.grammar.keywords:
                return [self.grammar.keywords[value]]
            elif value in self.grammar.soft_keywords:
                assert type in self.grammar.tokens
                return [
                    self.grammar.soft_keywords[value],
                    self.grammar.tokens[type],
                ]

        ilabel = self.grammar.tokens.get(type)
        if ilabel is None:
            raise ParseError("bad token", type, value, context)
        return [ilabel]

    def shift(self, type: int, value: Text, newstate: int, context: Context) -> None:
        """Shift a token.  (Internal)"""
        if self.is_backtracking:
            dfa, state, _ = self.stack[-1]
            self.stack[-1] = (dfa, newstate, DUMMY_NODE)
        else:
            dfa, state, node = self.stack[-1]
            rawnode: RawNode = (type, value, context, None)
            newnode = convert(self.grammar, rawnode)
            assert node[-1] is not None
            node[-1].append(newnode)
            self.stack[-1] = (dfa, newstate, node)

    def push(self, type: int, newdfa: DFAS, newstate: int, context: Context) -> None:
        """Push a nonterminal.  (Internal)"""
        if self.is_backtracking:
            dfa, state, _ = self.stack[-1]
            self.stack[-1] = (dfa, newstate, DUMMY_NODE)
            self.stack.append((newdfa, 0, DUMMY_NODE))
        else:
            dfa, state, node = self.stack[-1]
            newnode: RawNode = (type, None, context, [])
            self.stack[-1] = (dfa, newstate, node)
            self.stack.append((newdfa, 0, newnode))

    def pop(self) -> None:
        """Pop a nonterminal.  (Internal)"""
        if self.is_backtracking:
            self.stack.pop()
        else:
            popdfa, popstate, popnode = self.stack.pop()
            newnode = convert(self.grammar, popnode)
            if self.stack:
                dfa, state, node = self.stack[-1]
                assert node[-1] is not None
                node[-1].append(newnode)
            else:
                self.rootnode = newnode
                self.rootnode.used_names = self.used_names
