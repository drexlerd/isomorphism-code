from src.util.misc import update_dict


def experiments():
    base = dict(
        pipeline="sketch",
    )

    exps = dict()

    strips_base = update_dict(
        base
    )

    exps["release"] = update_dict(
        strips_base,
    )

    exps["debug"] = update_dict(
        strips_base,
        generate_features=False,
        add_features=["b_empty(c_and(c_primitive(at-robby,0),c_one_of(rooma)))",  # robot at room b
                      "n_count(r_primitive(carry,0,1))",  # 4 num balls that the robot carries
                      "n_count(r_diff(r_primitive(at_g,0,1), r_primitive(at,0,1)))",  # 4 num misplaced balls, i.e., num balls at roomb
                      "b_empty(r_diff(r_primitive(at_g,0,1), r_primitive(at,0,1)))",  # goal separating feature
        ],
    )
    return exps
