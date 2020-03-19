import re
import Token
from typing import AnyStr, Dict, Union, Optional

import discord
from discord.ext import commands


class MyBot:
    COM_PARSER = re.compile(
        r"^name:\s*(?P<name>[A-ZА-Я]\w+\s[A-ZА-Я]\w+)(?:[\s,;]+role:\s*(?P<role>(?:stud)|(?:teacher)))?$")
    N_PARSER = re.compile(r"^num:\s*(?P<num>\d+)$")
    WELCOME_MSG = "hello, {member.mention}.\n" \
                  "I'm bot, please write message to the channel that you recently joined in the following pattern:\n" \
                  "!reg name:*[your name and surname from the capital latter]*, role:*[stud|teacher]*\n" \
                  "or, if you are a stud, just !nreg num:*[your number in list]*\n" \
                  "to see list send !list\n" \
                  "it is needed to register you here\n" \
                  "если ваше сообщение исчезло, имя изменилось и вы снова видите это - все хорошо, вы зарегистрированы"

    def __init__(self) -> None:
        super().__init__()
        self.TOKEN = Token.token

        self.bot = commands.Bot(command_prefix='!')

        def args_parser(arg: AnyStr) -> Optional[Dict[str, str]]:
            matched = self.COM_PARSER.match(arg)
            if not matched:
                return None
            else:
                return {"name": matched.group("name"), "role": matched.group("role")}

        def nreg_parser(s: str) -> Optional[int]:
            matched = self.N_PARSER.match(s)
            return None if not matched else int(matched.group("num"))

        async def set_member_opts(member: discord.Member, args: Dict[str, str]):
            if len(args) == 0:
                return
            if isinstance(member.guild, discord.Guild):
                arg_list = {"reason": "bot command", "nick": args["name"]}
                if len(member.roles) == 1:
                    if args["role"]:
                        arg_list.setdefault("roles",
                                            [member.guild.roles[1] if args["role"] == "stud" else member.guild.roles[
                                                2]])
                await member.edit(**arg_list)

        @self.bot.command(description="registration of user",
                          pass_context=True)
        async def reg(ctx: commands.context.Context, *, args: args_parser = {}):
            if not args:
                await ctx.send("invalid message")  # отправляем обратно аргумент
            else:
                try:
                    await set_member_opts(ctx.author, args)
                except BaseException:
                    return
                else:
                    try:
                        await clear(ctx)
                    except Exception:
                        pass
                    await ctx.author.create_dm()
                    await ctx.author.dm_channel.send("ok, now you are registered and changes ara accepted\n"
                                                     "to change your name just repeat command")

        @self.bot.event
        async def on_member_join(member):
            await member.create_dm()
            await member.dm_channel.send(self.WELCOME_MSG.format(member=member))

        @self.bot.command()
        async def clear(ctx):
            try:
                msgs = await ctx.channel.history().flatten()
                await ctx.channel.delete_messages(msgs[:-1])
            except Exception:
                pass

        @self.bot.command()
        async def nreg(ctx, *, arg: nreg_parser):
            try:
                with open("list.txt", 'r', encoding='utf-8') as fi:
                    f = [i for i in fi]
                    await reg(ctx,
                              args=args_parser('name:{name[2]} {name[1]}, role:stud'.format(name=f[arg - 1].split())))
            except Exception:
                await ctx.send('something wrong')

        @self.bot.command()
        async def list(ctx):
            with open("list.txt", 'r', encoding='utf-8') as fi:
                await ctx.send(fi.read())

        @self.bot.command()
        async def force_nreg(ctx, mem: discord.Member, num: int):
            if not ctx.author.permissions_in(ctx.channel).is_superset(discord.Permissions(1 << 3)):
                await ctx.send("no rights")
                return
            try:
                with open("list.txt", 'r', encoding='utf-8') as fi:
                    f = [i for i in fi]
                    await set_member_opts(mem, args_parser(
                        'name:{name[2]} {name[1]}, role:stud'.format(name=f[num - 1].split())))
            except Exception:
                await ctx.send('something wrong')

        @self.bot.command()
        async def force_reg(ctx, mem: discord.Member, *, arg: args_parser):
            if not ctx.author.permissions_in(ctx.channel).is_superset(discord.Permissions(1 << 3)):
                await ctx.send("no rights")
                return
            try:
                await set_member_opts(mem, arg)
            except Exception:
                await ctx.send('something wrong')

    def run(self):
        self.bot.run(self.TOKEN)

# it's main
if __name__ == '__main__':
    MyBot().run()
