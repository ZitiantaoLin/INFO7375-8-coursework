import drawing_base as base
import eyespan_v2_draw as v2
if __name__=='__main__':
    base.render_frame=v2.render_frame
    base.ROOT=v2.ROOT
    base.main()
